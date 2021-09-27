# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)   # 目标数据
arcpy.env.workspace = os.path.dirname(infc)
basin = arcpy.GetParameterAsText(1)   # 流域
temp = os.path.dirname(infc)
# 存临时数据的gdb
if temp[-3:] == "gdb":
    tempGdb = temp
else:
    tempGdb = str(temp)+"\\temp.gdb"
    arcpy.CreateFileGDB_management(temp, "temp.gdb")
temp_point = tempGdb + "\\river_to_point"  # 存河流转的点用
Kjlj = tempGdb + "\\kongjianlianjie"  # 空间连接用
tempShp = tempGdb + "\\chouxi"  # 抽稀用

# 按属性选择需要输入一个图层，先把河流数据弄成一个图层
arcpy.MakeFeatureLayer_management(infc, "river")
# 先选中要处理的河
print "选择待处理的河流"
arcpy.AddMessage("选择待处理的河流")
rivers = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION", """"state" = '1'""")
# 复制选中的河数据到临时gdb里，准备抽稀（概化）
print "复制到临时文件"
arcpy.AddMessage("复制到临时文件")
arcpy.CopyFeatures_management("river", tempShp, "#", "0", "0", "0")
# 抽抽稀两次
arcpy.AddMessage("正在抽稀……")
print "正在抽稀……"
arcpy.Generalize_edit(tempShp, "#")
# 要素转点
print "要素转点……"
arcpy.AddMessage("要素转点……")
arcpy.FeatureVerticesToPoints_management(tempShp,temp_point,"ALL")
# 空间连接
print "空间连接……"
arcpy.AddMessage("空间连接……")
arcpy.SpatialJoin_analysis(temp_point, basin, Kjlj, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "WITHIN", "#", "#")
# 统计每个sid、流域组合出现的次数，同一sid中出现次数最多的就是该河流所属流域
print "开始读取……"
arcpy.AddMessage("开始读取……")
searchCursor = arcpy.da.SearchCursor(Kjlj, ("OSID", "NAME_1"))
dic = {}
for osid , basin in searchCursor:
    if osid not in dic.keys():
        dic[osid] = {}
    elif basin not in dic[osid].keys():
        dic[osid][basin] = 1
    else:
        dic[osid][basin] += 1
# 统计每个sid中出现最多次的流域
dic2 = {}
print "开始统计……"
arcpy.AddMessage("开始统计……")
for osid, basin in dic.items():
    if osid not in dic2.keys():
        dic2[osid] = {}
    dic2[osid] = max(basin,key=basin.get)
# 更新回去~
updateCursor = arcpy.da.UpdateCursor(infc, ("OSID", "SRNAME"),""""state" = '1'""")
for row in updateCursor:
    sid = row[0].encode('utf-8')
    row[1] = dic2[sid].encode('utf-8')
    updateCursor.updateRow(row)
    print "已处理osid为%s的河流,它的流域是%s" % (str(sid), str(row[1]))
    arcpy.AddMessage("已处理osid为%s的河流,它的流域是%s" % (str(sid), str(row[1])))
print "已完成，正在删除临时数据"
arcpy.AddMessage("已完成，正在删除临时数据")
arcpy.Delete_management(temp_point)
arcpy.Delete_management(Kjlj)
arcpy.Delete_management(tempShp)
if tempGdb != temp:
    arcpy.Delete_management(tempGdb)
del updateCursor
print "已完成所有步骤~"
arcpy.AddMessage("已完成所有步骤~")
# 完成啦~~
