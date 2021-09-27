# -*- coding: gb2312 -*-
import arcpy
import os

path = arcpy.GetParameterAsText(0)  # 待处理数据
workspace = os.path.dirname(path)
arcpy.env.workspace = workspace
temp = workspace + "\\1.shp"
arcpy.MakeFeatureLayer_management(path, "river_pro")
filename = os.path.basename(path)
proNew = arcpy.SelectLayerByAttribute_management("river_pro", "NEW_SELECTION", """"state" = '1'""")

# 投影到China_2000GCS_Albers
arcpy.Project_management(proNew, temp,
                         "PROJCS['China_2000GCS_Albers',GEOGCS['GCS_CGCS_2000',DATUM['D_CGCS_2000',SPHEROID["
                         "'CGCS_2000',6378137.0,298.257222101]], PRIMEM['Greenwich',0.0],UNIT['Degree',"
                         "0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0], "
                         "PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',103.0],PARAMETER["
                         "'Standard_Parallel_1',28.0], PARAMETER['Standard_Parallel_2',32.0],PARAMETER["
                         "'Latitude_Of_Origin',24.0],UNIT['Meter',1.0]]", "#",
                         "GEOGCS['China Geodetic Coordinate System 2000',DATUM['China_2000',SPHEROID['CGCS2000',"
                         "6378137.0,298.257222101]], "
                         "PRIMEM['Greenwich',0.0],UNIT['degree',0.0174532925199433]]")
# 计算长度
arcpy.CalculateField_management(temp, "RLEN", "!shape.length@kilometers!", "PYTHON_9.3", "#")
# 用sid连接回来
arcpy.management.AddJoin("river_pro", "SID", temp, "SID")
# 赋值
arcpy.CalculateField_management("river_pro", str(filename.split(".")[0]) + ".RLEN", "!1.RLEN! ", "PYTHON_9.3", "#")
# 删除临时数据
arcpy.Delete_management(temp, "ShapeFile")
