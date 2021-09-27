# -*- coding: cp936 -*-
import arcpy
import math
import os

infc = arcpy.GetParameterAsText(0)  # 目标数据
arcpy.env.workspace = os.path.dirname(infc)
region = arcpy.GetParameterAsText(1)  # 行政区划

# 把行政区划的pac和名称搞出来
searchCursor = arcpy.da.SearchCursor(region, ("PAC", "NAME"))
region = {}
for pac, name in searchCursor:
    region[pac] = name
del searchCursor
# 对应的更新进河段名称里
updateCursor = arcpy.da.UpdateCursor(infc, ("NAME", "RNAME", "PAC"),""""state" = '1'""")
for row in updateCursor:
    if len(row[2]) < 12:
        row[0] = row[1].encode('utf-8') + region[row[2]].encode('utf-8') + "段"
        updateCursor.updateRow(row)
        print "已处理%s" % str(row[0])
        arcpy.AddMessage("已处理%s" % str(row[0]))
    else:
        row[0] = row[1].encode('utf-8') + region[row[2][:9]].encode('utf-8') + "段(村级)"
        updateCursor.updateRow(row)
        print "已处理%s" % str(row[0])
        arcpy.AddMessage("已处理%s" % str(row[0]))
del updateCursor
