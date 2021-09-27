# -*- coding: cp936 -*-
import arcpy
import os

inputs = arcpy.GetParameterAsText(0)
dirs = inputs.split(";")

pro = city = county = town = village = ""

# 自然数顺序赋值
step=0


def aa():
   global step,code
   pstart=1
   pinterval=1
   if(step==0):
      step=pstart
   else:
      step=step+pinterval
   code='%05.0f'%step
   return code


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
# 存空间连接后输出的数据的gdb
if temp[-3:] == "gdb":
    outGdb = temp
else:
    outGdb = str(temp)+"\\out.gdb"
    arcpy.CreateFileGDB_management(temp, "out.gdb")
paths = [pro,city,county,town,village]
levels = ["pro_id","city_id","county_id","town_id","village_id"]
for path,level in zip(paths,levels):
    arcpy.AddField_management(path, level, "TEXT")
    updateCursor = arcpy.da.UpdateCursor(path, (level))
    for row in updateCursor:
        row[0] = aa()
        updateCursor.updateRow(row)
    step = 0

arcpy.AddMessage("市连省……")
pfieldmappings = arcpy.FieldMappings()
pfieldmappings.addTable(city)
tempp = arcpy.FieldMappings()
tempp.addTable(pro)
pro_id = tempp.findFieldMapIndex("pro_id")
fieldmap = tempp.getFieldMap(pro_id)
pfieldmappings.addFieldMap(fieldmap)
arcpy.SpatialJoin_analysis(city,pro,outGdb+"\\a_hydl_city","JOIN_ONE_TO_ONE","KEEP_ALL",pfieldmappings,"WITHIN","#","#")

arcpy.AddMessage("县连市……")
cfieldmappings = arcpy.FieldMappings()
cfieldmappings.addTable(county)
tempp = arcpy.FieldMappings()
tempp.addTable(city)
city_id = tempp.findFieldMapIndex("city_id")
fieldmap = tempp.getFieldMap(city_id)
cfieldmappings.addFieldMap(fieldmap)
arcpy.SpatialJoin_analysis(county,city,outGdb+"\\a_hydl_county","JOIN_ONE_TO_ONE","KEEP_ALL",cfieldmappings,"WITHIN","#","#")

arcpy.AddMessage("镇连县……")
cofieldmappings = arcpy.FieldMappings()
cofieldmappings.addTable(town)
tempp = arcpy.FieldMappings()
tempp.addTable(county)
county_id = tempp.findFieldMapIndex("county_id")
fieldmap = tempp.getFieldMap(county_id)
cofieldmappings.addFieldMap(fieldmap)
arcpy.SpatialJoin_analysis(town,county,outGdb+"\\a_hydl_town","JOIN_ONE_TO_ONE","KEEP_ALL",cofieldmappings,"WITHIN","#","#")

arcpy.AddMessage("村连镇……")
tfieldmappings = arcpy.FieldMappings()
tfieldmappings.addTable(village)
tempp = arcpy.FieldMappings()
tempp.addTable(town)
town_id = tempp.findFieldMapIndex("town_id")
fieldmap = tempp.getFieldMap(town_id)
tfieldmappings.addFieldMap(fieldmap)
arcpy.SpatialJoin_analysis(village,town,outGdb+"\\a_hydl_village","JOIN_ONE_TO_ONE","KEEP_ALL",tfieldmappings,"WITHIN","#","#")

arcpy.AddMessage("省……")
arcpy.CopyFeatures_management(pro, outGdb+"\\a_hydl_pro")
