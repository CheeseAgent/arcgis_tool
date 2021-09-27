# -*- coding: cp936 -*-
import arcpy
import os

inputs = arcpy.GetParameterAsText(0)
dirs = inputs.split(";")

pro = city = county = town = village = ""


for path in dirs:
    if "pro" in path:
        pro = path
    elif "city" in path:
        city = path
    elif "county" in path:
        county = path
    elif "town" in path:
        town = path
    elif "village" in path:
        village = path
temp = os.path.dirname(pro)


def new_level(path,level):
    updateCursor = arcpy.da.UpdateCursor(path, ("LEVEL"), """"state" = '1'""")
    for row in updateCursor:
        row[0] = level
        updateCursor.updateRow(row)
    del updateCursor


new_level(pro,"省级")
new_level(city,"市级")
new_level(county,"县级")
new_level(town,"乡镇级")
new_level(village,"村级")
