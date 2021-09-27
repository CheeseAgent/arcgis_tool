# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)  # Ŀ������
workspace = os.path.dirname(infc)
edit = arcpy.da.Editor(workspace)
edit.startEditing(False, True)
edit.startOperation()
path = workspace
region = arcpy.GetParameterAsText(1)  # ��������
temp = os.path.dirname(infc)
# ����ʱ���ݵ�gdb
if temp[-3:] == "gdb":
    tempGdb = temp
else:
    tempGdb = str(temp)+"\\temp.gdb"
    arcpy.CreateFileGDB_management(temp, "temp.gdb")
output = tempGdb + "/point"  # ����ƽ�������ĵ���,���Ҫ���Ƚ��ö����ֶ�Ҫ��
Kjlj = tempGdb + "/kongjianlianjie"  # �ռ�������
tempShp = tempGdb + "/chouxi"  # ��ϡ��
rights = path + "rights.shp"  # ������Ÿ��Ƴ����Ľ�ӵģ��ӹ����Ұ�


def CopyParallel(plyP, sid):  # �������������Ӧsid����������ÿһ���߶��е�ֱ�������ƽ�ƺ�Ĵ�sid�����ҷ������Եĵ��б�
    part = plyP.getPart(0)
    lArray = arcpy.Array()
    rArray = arcpy.Array()
    temp = []
    for index in range(len(part) - 1):
        ptX0 = part[index]
        ptX1 = part[index + 1]
        ptX = arcpy.Point(float((ptX1.X + ptX0.X) / 2), float((ptX1.Y + ptX0.Y) / 2))  # ȡ�߶��е�
        dX = float(ptX1.X) - float(ptX0.X)
        dY = float(ptX1.Y) - float(ptX0.Y)
        lenV = math.hypot(dX, dY)  # sqrt(x*x + y*y)
        sX = -dY * 0.0015 / lenV  # ���Ǻ���~����
        sY = dX * 0.0015 / lenV
        leftP = (ptX.X + sX, ptX.Y + sY)
        rightP = (ptX.X - sX, ptX.Y - sY)
        temp_left = (leftP, sid, 'L')
        temp_right = (rightP, sid, 'R')
        temp.append(temp_left)
        temp.append(temp_right)
    return temp


# ������ѡ����Ҫ����һ��ͼ�㣬�ȰѺӶ�����Ū��һ��ͼ��
arcpy.MakeFeatureLayer_management(infc, "river")
print "ѡ����"
# ��ѡ��Ҫ����Ľ��
boundaryrivers = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION",
                                                         """"BOUNDARYRI" = 1 and "state" = '1'""")
# ����ѡ�еĽ�����ݵ���ʱgdb�׼����ϡ���Ż���
arcpy.CopyFeatures_management("river", tempShp, "#", "0", "0", "0")
# ��ϡ
print "��ʼ��ϡ"
arcpy.AddMessage("��ʼ��ϡ")
arcpy.Generalize_edit(tempShp, "#")
# �ѳ�ϡ�������ȫ����һ�飬�����ǵ�ƽ�������ĵ㣬����points��
points = []
searchCursor = arcpy.da.SearchCursor(tempShp, ("Shape@", "SID"))
for shp, sid in searchCursor:
    t = CopyParallel(shp, sid)
    # �����t��һ���кܶ����б�����ѭ���𿪵��������ķ���points��
    for p in t:
        points.append(p)
del searchCursor
# д����ʱgdb���point�׼���ռ�������
# �ȴ���Ҫ���࣬�����Ҫ���ֶ�
arcpy.CreateFeatureclass_management(tempGdb,"point","POINT","#","DISABLED","DISABLED",
                                    "GEOGCS['China Geodetic Coordinate System 2000',DATUM['China_2000',"
                                    "SPHEROID['CGCS2000',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],"
                                    "UNIT['degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;"
                                    "-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision","#","0","0","0")
arcpy.AddField_management(output,"SID","TEXT")
arcpy.AddField_management(output,"SIDE","TEXT")
# д��
with arcpy.da.InsertCursor(output, ("SHAPE@XY", "SID", "SIDE")) as cursor:
    for point in points:
        print point
        cursor.insertRow(point)
del cursor
edit.stopOperation()
edit.stopEditing(True)
# ������sid�����ұ�־�ĵ��������������пռ�����
arcpy.AddMessage("��ʼ�ռ�����")
arcpy.SpatialJoin_analysis(output, region, Kjlj, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "WITHIN", "#", "#")
# ͳ��ÿ��sid��pac��side��ϳ��ֵĴ�����ͬһsid�г��ִ��������������ǽ�����ҵ���������
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
# ͳ��ÿ��sid���������߷ֱ�������ε�pac
dic2 = {}
for sid, sidvalue in dic.items():
    if sid not in dic2.keys():
        dic2[sid] = {}
    for side, sidevalue in sidvalue.items():
        if side not in dic2[sid].keys():
            dic[sid][side] = {}
        dic2[sid][side] = max(sidevalue,key=sidevalue.get)
del searchCursor
# ��ԭʼ�������ִ�ı�־Ϊ��ӵĺӶ�ȫ�������󰶸���
updateCursor = arcpy.da.UpdateCursor(infc, ("SID", "PAC", "PAC2", "SIDE"),""""BOUNDARYRI" = 1 and "state" = '1'""")
for row in updateCursor:
    sid = row[0]
    row[1] = dic2[sid]['L']
    row[2] = dic2[sid]['R']
    row[3] = "��"
    updateCursor.updateRow(row)
    print "�Ѵ���sidΪ%s�ĺӶε�����" % str(sid)
    arcpy.AddMessage("�Ѵ���sidΪ%s�ĺӶε�����" % str(sid))
# ѡ�����е���߽��
lefts = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION",
                                                """"BOUNDARYRI" = 1 and "state" = '1'""")
del updateCursor
# �������Ƴ�����һ����ʱshp
arcpy.CopyFeatures_management(lefts, rights)
# ����Ϊ�Ұ�����
updateCursor = arcpy.da.UpdateCursor(rights, ("SID", "PAC", "PAC2", "SIDE"))
for row in updateCursor:
    pac = row[2]
    pac2 = row[1]
    row[1] = pac
    row[2] = pac2
    row[3] = "�Ұ�"
    updateCursor.updateRow(row)
    print "�Ѵ���sidΪ%s�ĺӶε��Ұ��" % str(row[0])
    arcpy.AddMessage("�Ѵ���sidΪ%s�ĺӶε��Ұ��" % str(row[0]))
del updateCursor
# ���ƻ�ȥ~���~~
arcpy.Append_management(rights,infc,"TEST","#","#")
print "����ɾ����ʱ����"
arcpy.AddMessage("����ɾ����ʱ����")
arcpy.Delete_management(output)
arcpy.Delete_management(Kjlj)
arcpy.Delete_management(tempShp)
arcpy.Delete_management(rights)
if tempGdb != temp:
    arcpy.Delete_management(tempGdb)
print "��������в���~"
arcpy.AddMessage("��������в���~")
# �����ܳ���pac��pac2��ͬ�������Ҫô����boundaryriver����ˣ�������Ӧ���ǽ�ӣ�Ҫô������һ�����������̫ϸ���ˣ������ĵ�ɳ�ȥ��û�ܶ���
# ���ֹ���ֻ���ֶ��ģ���������arcgis���ֶμ�������pac��pac2��ͬ�ĵ�vb���
# d = 1
# If ([BOUNDARYRI] = 1) and ([PAC] = [PAC2]) then
#      d = 999
# End If
