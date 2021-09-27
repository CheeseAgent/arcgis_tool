# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)  # Ŀ������
arcpy.env.workspace = os.path.dirname(infc)
region = arcpy.GetParameterAsText(1)  # ��������

# ������������pac�����Ƹ����
searchCursor = arcpy.da.SearchCursor(region, ("PAC", "NAME"))
region = {}
for pac, name in searchCursor:
    region[pac] = name
del searchCursor
# ��Ӧ�ĸ��½��Ӷ�������
updateCursor = arcpy.da.UpdateCursor(infc, ("NAME", "RNAME", "PAC"),""""state" = '1'""")
for row in updateCursor:
    if len(row[2]) < 12:
        row[0] = row[1].encode('utf-8') + region[row[2]].encode('utf-8') + "��"
        updateCursor.updateRow(row)
        print "�Ѵ���%s" % str(row[0])
        arcpy.AddMessage("�Ѵ���%s" % str(row[0]))
    else:
        row[0] = row[1].encode('utf-8') + region[row[2][:9]].encode('utf-8') + "��(�弶)"
        updateCursor.updateRow(row)
        print "�Ѵ���%s" % str(row[0])
        arcpy.AddMessage("�Ѵ���%s" % str(row[0]))
del updateCursor
