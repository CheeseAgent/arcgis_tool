# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)   # Ŀ������
arcpy.env.workspace = os.path.dirname(infc)
basin = arcpy.GetParameterAsText(1)   # ����
temp = os.path.dirname(infc)
# ����ʱ���ݵ�gdb
if temp[-3:] == "gdb":
    tempGdb = temp
else:
    tempGdb = str(temp)+"\\temp.gdb"
    arcpy.CreateFileGDB_management(temp, "temp.gdb")
temp_point = tempGdb + "\\river_to_point"  # �����ת�ĵ���
Kjlj = tempGdb + "\\kongjianlianjie"  # �ռ�������
tempShp = tempGdb + "\\chouxi"  # ��ϡ��

# ������ѡ����Ҫ����һ��ͼ�㣬�ȰѺ�������Ū��һ��ͼ��
arcpy.MakeFeatureLayer_management(infc, "river")
# ��ѡ��Ҫ����ĺ�
print "ѡ�������ĺ���"
arcpy.AddMessage("ѡ�������ĺ���")
rivers = arcpy.SelectLayerByAttribute_management("river", "NEW_SELECTION", """"state" = '1'""")
# ����ѡ�еĺ����ݵ���ʱgdb�׼����ϡ���Ż���
print "���Ƶ���ʱ�ļ�"
arcpy.AddMessage("���Ƶ���ʱ�ļ�")
arcpy.CopyFeatures_management("river", tempShp, "#", "0", "0", "0")
# ���ϡ����
arcpy.AddMessage("���ڳ�ϡ����")
print "���ڳ�ϡ����"
arcpy.Generalize_edit(tempShp, "#")
# Ҫ��ת��
print "Ҫ��ת�㡭��"
arcpy.AddMessage("Ҫ��ת�㡭��")
arcpy.FeatureVerticesToPoints_management(tempShp,temp_point,"ALL")
# �ռ�����
print "�ռ����ӡ���"
arcpy.AddMessage("�ռ����ӡ���")
arcpy.SpatialJoin_analysis(temp_point, basin, Kjlj, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "WITHIN", "#", "#")
# ͳ��ÿ��sid��������ϳ��ֵĴ�����ͬһsid�г��ִ������ľ��Ǹú�����������
print "��ʼ��ȡ����"
arcpy.AddMessage("��ʼ��ȡ����")
searchCursor = arcpy.da.SearchCursor(Kjlj, ("OSID", "NAME_1"))
dic = {}
for osid , basin in searchCursor:
    if osid not in dic.keys():
        dic[osid] = {}
    elif basin not in dic[osid].keys():
        dic[osid][basin] = 1
    else:
        dic[osid][basin] += 1
# ͳ��ÿ��sid�г������ε�����
dic2 = {}
print "��ʼͳ�ơ���"
arcpy.AddMessage("��ʼͳ�ơ���")
for osid, basin in dic.items():
    if osid not in dic2.keys():
        dic2[osid] = {}
    dic2[osid] = max(basin,key=basin.get)
# ���»�ȥ~
updateCursor = arcpy.da.UpdateCursor(infc, ("OSID", "SRNAME"),""""state" = '1'""")
for row in updateCursor:
    sid = row[0].encode('utf-8')
    row[1] = dic2[sid].encode('utf-8')
    updateCursor.updateRow(row)
    print "�Ѵ���osidΪ%s�ĺ���,����������%s" % (str(sid), str(row[1]))
    arcpy.AddMessage("�Ѵ���osidΪ%s�ĺ���,����������%s" % (str(sid), str(row[1])))
print "����ɣ�����ɾ����ʱ����"
arcpy.AddMessage("����ɣ�����ɾ����ʱ����")
arcpy.Delete_management(temp_point)
arcpy.Delete_management(Kjlj)
arcpy.Delete_management(tempShp)
if tempGdb != temp:
    arcpy.Delete_management(tempGdb)
del updateCursor
print "��������в���~"
arcpy.AddMessage("��������в���~")
# �����~~
