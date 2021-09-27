# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)  # 目标数据
workspace = os.path.dirname(infc)
edit = arcpy.da.Editor(workspace)
edit.startEditing(False, True)
edit.startOperation()
path = workspace
region = arcpy.GetParameterAsText(1)  # 行政区划
temp = os.path.dirname(infc)
# 存临时数据的gdb
if temp[-3:] == "gdb":
    tempGdb = temp
else:
    tempGdb = str(temp)+"\\temp.gdb"
    arcpy.CreateFileGDB_management(temp, "temp.gdb")
output = tempGdb + "/point"  # 存界河平行外扩的点用,这个要事先建好而且字段要对
Kjlj = tempGdb + "/kongjianlianjie"  # 空间连接用
tempShp = tempGdb + "/chouxi"  # 抽稀用
rights = path + "rights.shp"  # 用来存放复制出来的界河的，加工成右岸


def CopyParallel(plyP, sid):  # 输入多段线与其对应sid，返回它的每一段线段中点分别向左右平移后的带sid与左右方向属性的点列表
    part = plyP.getPart(0)
    lArray = arcpy.Array()
    rArray = arcpy.Array()
    temp = []
    for index in range(len(part) - 1):
        ptX0 = part[index]
        ptX1 = part[index + 1]
        ptX = arcpy.Point(float((ptX1.X + ptX0.X) / 2), float((ptX1.Y + ptX0.Y) / 2))  # 取线段中点
        dX = float(ptX1.X) - float(ptX0.X)
        dY = float(ptX1.Y) - float(ptX0.Y)
        lenV = math.hypot(dX, dY)  # sqrt(x*x + y*y)
        sX = -dY * 0.0015 / lenV  # 三角函数~！！
        sY = dX * 0.0015 / lenV
        leftP = (ptX.X + sX, ptX.Y + sY)
        rightP = (ptX.X - sX, ptX.Y - sY)
        temp_left = (leftP, sid, 'L')
        temp_right = (rightP, sid, 'R')
        temp.append(temp_left)
        temp.append(temp_right)
    return temp


# 按属性选择需要输入一个图层，先把河段数据弄成一个图层
arcpy.MakeFeatureLayer_management(infc, "river")
print "选择界河"
# 先选中要处理的界河
boundaryrivers = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION",
                                                         """"BOUNDARYRI" = 1 and "state" = '1'""")
# 复制选中的界河数据到临时gdb里，准备抽稀（概化）
arcpy.CopyFeatures_management("river", tempShp, "#", "0", "0", "0")
# 抽稀
print "开始抽稀"
arcpy.AddMessage("开始抽稀")
arcpy.Generalize_edit(tempShp, "#")
# 把抽稀后的数据全部过一遍，生他们的平行外扩的点，存在points里
points = []
searchCursor = arcpy.da.SearchCursor(tempShp, ("Shape@", "SID"))
for shp, sid in searchCursor:
    t = CopyParallel(shp, sid)
    # 这里的t是一个有很多点的列表，得用循环拆开单个单个的放在points里
    for p in t:
        points.append(p)
del searchCursor
# 写入临时gdb里的point里，准备空间连接用
# 先创建要素类，添加需要的字段
arcpy.CreateFeatureclass_management(tempGdb,"point","POINT","#","DISABLED","DISABLED",
                                    "GEOGCS['China Geodetic Coordinate System 2000',DATUM['China_2000',"
                                    "SPHEROID['CGCS2000',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],"
                                    "UNIT['degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;"
                                    "-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision","#","0","0","0")
arcpy.AddField_management(output,"SID","TEXT")
arcpy.AddField_management(output,"SIDE","TEXT")
# 写入
with arcpy.da.InsertCursor(output, ("SHAPE@XY", "SID", "SIDE")) as cursor:
    for point in points:
        print point
        cursor.insertRow(point)
del cursor
edit.stopOperation()
edit.stopEditing(True)
# 将带有sid和左右标志的点与行政区划进行空间连接
arcpy.AddMessage("开始空间连接")
arcpy.SpatialJoin_analysis(output, region, Kjlj, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "WITHIN", "#", "#")
# 统计每个sid、pac、side组合出现的次数，同一sid中出现次数最多的两个就是界河左右的行政区划
searchCursor = arcpy.da.SearchCursor(Kjlj, ("SID", "PAC", "SIDE"))
dic = {}
for sid, pac, side in searchCursor:
    if sid not in dic.keys():
        dic[sid] = {}
        dic[sid][side] = {}
        dic[sid][side][pac] = 1
    elif side not in dic[sid].keys():
        dic[sid][side] = {}
        dic[sid][side][pac] = 1
    elif pac not in dic[sid][side].keys():
        dic[sid][side][pac] = 1
    else:
        dic[sid][side][pac] += 1
# 统计每个sid的左右两边分别出现最多次的pac
dic2 = {}
for sid, sidvalue in dic.items():
    if sid not in dic2.keys():
        dic2[sid] = {}
    for side, sidevalue in sidvalue.items():
        if side not in dic2[sid].keys():
            dic[sid][side] = {}
        dic2[sid][side] = max(sidevalue,key=sidevalue.get)
del searchCursor
# 把原始数据里现存的标志为界河的河段全部当成左岸更新
updateCursor = arcpy.da.UpdateCursor(infc, ("SID", "PAC", "PAC2", "SIDE"),""""BOUNDARYRI" = 1 and "state" = '1'""")
for row in updateCursor:
    sid = row[0]
    row[1] = dic2[sid]['L']
    row[2] = dic2[sid]['R']
    row[3] = "左岸"
    updateCursor.updateRow(row)
    print "已处理sid为%s的河段的左半边" % str(sid)
    arcpy.AddMessage("已处理sid为%s的河段的左半边" % str(sid))
# 选出所有单左边界河
lefts = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION",
                                                """"BOUNDARYRI" = 1 and "state" = '1'""")
del updateCursor
# 单独复制出来到一个临时shp
arcpy.CopyFeatures_management(lefts, rights)
# 更新为右岸属性
updateCursor = arcpy.da.UpdateCursor(rights, ("SID", "PAC", "PAC2", "SIDE"))
for row in updateCursor:
    pac = row[2]
    pac2 = row[1]
    row[1] = pac
    row[2] = pac2
    row[3] = "右岸"
    updateCursor.updateRow(row)
    print "已处理sid为%s的河段的右半边" % str(row[0])
    arcpy.AddMessage("已处理sid为%s的河段的右半边" % str(row[0]))
del updateCursor
# 复制回去~完成~~
arcpy.Append_management(rights,infc,"TEST","#","#")
print "正在删除临时数据"
arcpy.AddMessage("正在删除临时数据")
arcpy.Delete_management(output)
arcpy.Delete_management(Kjlj)
arcpy.Delete_management(tempShp)
arcpy.Delete_management(rights)
if tempGdb != temp:
    arcpy.Delete_management(tempGdb)
print "已完成所有步骤~"
arcpy.AddMessage("已完成所有步骤~")
# 存在跑出来pac和pac2相同的情况，要么就是boundaryriver填错了，本来不应该是界河，要么就是有一侧的行政区划太细长了，外扩的点飞出去了没能读到
# 这种估计只有手动改，下面是在arcgis里字段计算器找pac和pac2相同的的vb语句
# d = 1
# If ([BOUNDARYRI] = 1) and ([PAC] = [PAC2]) then
#      d = 999
# End If
