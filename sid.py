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


def get_newest(path):
    searchCursor = arcpy.da.SearchCursor(path, ("SID", "PAC","state"))
    dic = {}
    for sid, pac,state in searchCursor:
        if pac not in dic.keys():
            if state =="1":
                dic[pac] = 0
            else:
                dic[pac] = int(sid[-4:])
        elif state == "0" and int(sid[-4:]) > dic[pac]:
            dic[pac] = int(sid[-4:])
    del searchCursor
    arcpy.AddMessage("已生成%s的最新oid字典" % str(path))
    return dic


def new_oid(path, dic):
    updateCursor = arcpy.da.UpdateCursor(path, ("SID", "PAC"), """"state" = '1'""")
    for row in updateCursor:
        pac = row[1]
        oid = int(dic[pac]) + 1
        dic[pac] += 1
        for i in range(4-len(str(oid))):
            oid = "0"+str(oid)
        row[0] = str(pac[2:]) + str(oid)
        updateCursor.updateRow(row)
        print "新oid:%s" % str(row[0])
        arcpy.AddMessage("新oid:%s" % str(row[0]))
    del updateCursor


def sid_dic(path,self_id):
    searchCursor = arcpy.da.SearchCursor(path, ("SID", self_id))
    dic = {}
    for sid,self_id in searchCursor:
        if self_id not in dic.keys():
            dic[self_id] = sid
    del searchCursor
    arcpy.AddMessage("已生成%s的sid字典" % str(path))
    return dic


def update_new_sid(path,xx_id,u_dic):
    updateCursor = arcpy.da.UpdateCursor(path, ("SID",xx_id), """"state" = '1'""")
    for row in updateCursor:
        oid = row[0]
        upper_id = row[1]
        uppersid = u_dic[upper_id]
        sid = str(uppersid) + "-" + str(oid)
        row[0] = sid
        updateCursor.updateRow(row)
        print "新sid:%s" % str(row[0])
        arcpy.AddMessage("新sid:%s" % str(row[0]))
    del updateCursor


pro_dic = get_newest(pro)
city_dic = get_newest(city)
county_dic = get_newest(county)
town_dic = get_newest(town)

new_oid(pro,pro_dic)
new_oid(city,city_dic)
new_oid(county,county_dic)
new_oid(town,town_dic)

pro_sid = sid_dic(pro,"pro_id")
update_new_sid(city,"pro_id",pro_sid)
city_sid = sid_dic(city,"city_id")
update_new_sid(county,"city_id",city_sid)
county_sid = sid_dic(county,"county_id")
update_new_sid(town,"county_id",county_sid)
town_sid = sid_dic(town,"town_id")

updateCursor = arcpy.da.UpdateCursor(village, ("SID", "town_id"), """"state" = '1'""")
for row in updateCursor:
    row[0] = town_sid[row[1]]
    updateCursor.updateRow(row)
    print "新sid:%s" % str(row[0])
    arcpy.AddMessage("新sid:%s" % str(row[0]))
del updateCursor
