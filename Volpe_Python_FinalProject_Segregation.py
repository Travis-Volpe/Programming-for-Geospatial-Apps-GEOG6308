###############################################################################
# Author: Travis Volpe
# Date: 12/21/2016
#
#Description: This script calculates the segregation index for Washington DC
#               and for each ward based upon tract level data. The script starts
#               by making a table join with the wards as the target features and
#               tracts as the join features. This is used to gather population data
#               from the 2010 census.
#               The table is manually exported to an excel file and the census race
#               codes are change to names to ease confusion. Next the script uses
#               pandas to read this excel file and uses te assign function to
#               create new categories that represent the ratio of the population of
#               an ethnicity living in a ward to the population of that race living in DC.
#               These ratios are subtracted and assign is used to
#               create new colums that represent the differences.
#               The disimilarity index is than calculated in excel by summing
#               the differences for each ward and dividing this by 2.
#               steps are repeated to cacluate the dsilimarity index for the wards.
#               To calculate the ward level dismiliarity index the wards are spatially joined to the tracts
#               so that each tract has the value of the ward it is within attributed to it.
#               The other steps are repeated for this data to get ward level statistics.
#               Finally, these calculations are exported into ArcMap and joined with
#               the ward layer.
#
###############################################################################

#%%
# The script must be run cell by cell and cannot be run all at once.
# There are intermediate steps that manipulate some of the data tables that are used in the proceeding step.
# For example between steps 1 ans 2 the resulting join is manually exported into Excel
# and between steps 4 and 5 the Disimilarity index is manually calculated.

import arcpy
import pandas as pd
from pandas import DataFrame as df
import os


#%%
#STEP 1
# This cell uses a spatial join to connect the tract level census data from 2010
# to the wards shapefile for Washington, DC. This provides the population count
# for each racial group surveyed for each ward.

arcpy.env.workspace = r'S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\SegDisIndxFiles.gdb'
arcpy.env.overwriteOutput = True

#SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})
arcpy.SpatialJoin_analysis('Ward__2002.dbf', 'TractPly.dbf', r'S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\SegDisIndxFiles.gdb\WARDS2010c','JOIN_ONE_TO_ONE','KEEP_ALL','OBJECTID "OBJECTID",First,#,Ward__2002,OBJECTID,-1,-1;SHAPE_Leng "SHAPE_Leng" ,First,#,Ward__2002,SHAPE_Leng,-1,-1;SHAPE_Area "SHAPE_Area",First,#,Ward__2002,SHAPE_Area,-1,-1;GEOID "GEOID",First,#,TractPly2010,GEOID,-1,-1;P0010001 "P0010001",Sum,#,TractPly2010,P0010001,-1,-1;P0010003 "P0010003",Sum,#,TractPly2010,P0010003,-1,-1;P0010004 "P0010004" ,Sum,#,TractPly2010,P0010004,-1,-1;P0010006 "P0010006",Sum,#,TractPly2010,P0010006,-1,-1', 'INTERSECT', '#', '#')

#Step 1a: export SpatialJoin_analysis from ArcMap to Excel as a csv file

#%%
# STEP 2
# This cell opens and reads the excel file that was created in step 1a

#Sets the file that is to be opened
pd.read_excel( r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Wards_2010.xlsx")

# Establishes the directory
os.chdir(r'S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data')

#Defines disindx as the excel file that was read
disindx = pd.read_excel('Wards_2010.xlsx')

# Sets the number of rows that will be used to 9
disindx.head(n=9)


#%%
#STEP 3
# This cell calculate the proportion of the population of a race in a ward to
#   the total population of that race in the city. The assign function  from pandas
#   is used to create new columns that are populated with these calculations.

disindx_assign1 = (disindx.assign(wi_WT = disindx['White(i)'] / disindx['White(T)'])
    .assign(bi_BT = disindx['Black(i)'] / disindx['Black(T)'])
    .assign(ai_AT = disindx['Asian(i)'] / disindx['Asian(T)'])
        .head(n=9))

#This part of the cell creates an excel file populated with the dated calculated from
#   the disindx_assign1 function.
writer = pd.ExcelWriter(r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Wards_2010_DCcounts.xlsx")
disindx_assign1.to_excel(writer,)
writer.save()

#%%
#STEP 4
# This cell calculate the absolute values of the proportion of one race to another in the wards.
# The assign function from pandas is used to create new columns that are populated with these calculations.

# Reads excel file
pd.read_excel( r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Wards_2010_DCcounts.xlsx")

#Caculates proportions and uses assign to create new columns
disindx_assign2 = (df.abs(disindx_assign1.assign(AbsWB = disindx_assign1[ 'wi_WT' ] - disindx_assign1[ 'bi_BT' ])
    .assign(AbsWA = disindx_assign1[ 'wi_WT' ] - disindx_assign1[ 'ai_AT' ])
    #.assign(AbsBW = disindx_assign1[ 'bi_BT' ] - disindx_assign1[ 'wi_WT' ]) : Not needed used to confim absolute value was working
    .assign(AbsBA = disindx_assign1[ 'bi_BT' ] - disindx_assign1[ 'ai_AT' ])
            .head(n=9)))

#Creates an excel file populated with the dated calculated from the disindx_assign2 function.
writer = pd.ExcelWriter(r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Wards_2010_DCratio.xlsx")
disindx_assign2.to_excel(writer,)
writer.save()

# Step 4a: in the exported excel file calaculate the disilimarity index
# D = 1/2(SUM(Abs_Races))
# as the disilimarity index is a global measure and in this context is only begining
# calaculated for the entire city it did not seem necessary to use pandas to do this.
# D = ...

#%%
#STEP 5
# This cell uses a spatial join to connect the wards shapefile
#   to the tract shapefile for Washington, DC. This assigns each tract to the
#   ward that it is within.
arcpy.env.workspace = r'S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\SegDisIndxFiles.gdb'
arcpy.env.overwriteOutput = True

#SpatialJoin_analysis (target_features, join_features, out_feature_class, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})
arcpy.SpatialJoin_analysis('TractPly.dbf', 'Ward__2002.dbf', r'S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\SegDisIndxFiles.gdb\TRACTS2010b','JOIN_ONE_TO_ONE','KEEP_ALL','TRACT "TRACT",First,#,TractPly2010,TRACT,-1,-1;GEOID "GEOID" ,First,#,TractPly2010,GEOID,-1,-1;P0010001 "P0010001" ,First,#,TractPly2010,P0010001,-1,-1;P0010003 "P0010003" ,First,#,TractPly2010,P0010003,-1,-1;P0010004 "P0010004" ,First,#,TractPly2010,P0010004,-1,-1;WARD_ID "WARD_ID" ,First,#,Ward__2002,WARD_ID,-1,-1', 'INTERSECT', '#', '#')

#%%
#STEP 6
#Defines disindx_wards as the excel file that was read
disindx_wards = pd.read_excel('Tracts_Wards_aug.xlsx')

# Sets the number of rows that will be used to 180
disindx_wards.head(n=180)

#%%
#STEP 7
#This cell calculate the proportion of the population  of a race in a ward to
#   the total population of that race in the city. The assign function from pandas
#   is used to create new columns that are populated with these calauclations.

#Calculate the the proportion the the population of a race in a ward to the total population of that race in the city
disindx_wards_tW = (disindx_wards.assign(wt_WW = disindx_wards['White(t)'] / disindx_wards['White(W)'])
    .assign(bt_BW = disindx_wards['Black(t)'] / disindx_wards['Black(W)'])
    .assign(at_AW = disindx_wards['Asian(t)'] / disindx_wards['Asian(W)'])
        .head(n=180))

#Creates an excel file populated with the dated calculated from the disindx_wards_tW function.
writer = pd.ExcelWriter(r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Tracts_Wards2010_tWa.xlsx")
disindx_wards_tW.to_excel(writer,)
writer.save()


#%%
#STEP 8
# This cell calculate the absolute values of the proportion of one race to another in the tracts
#   and adds columns that are populated with these values.
pd.read_excel( r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Tracts_Wards2010_tWa.xlsx")


# Caculates diferences and uses assign to create new columns
disindx_wards_ratios = (df.abs(disindx_wards_tW.assign(AbsWB = disindx_wards_tW[ 'wt_WW' ] - disindx_wards_tW[ 'bt_BW' ])
    .assign(AbsWA = disindx_wards_tW[ 'wt_WW' ] - disindx_wards_tW[ 'at_AW' ])
    #.assign(AbsBW = disindx_assign1[ 'bi_BT' ] - disindx_assign1[ 'wi_WT' ]) : Not needed used to confim absolute value was working
    .assign(AbsBA = disindx_wards_tW[ 'bt_BW' ] - disindx_wards_tW[ 'at_AW' ])
            .head(n=180)))

#Creates an excel file populated with the dated calculated from the disindx_wards_ratios function.
writer = pd.ExcelWriter(r"S:\GEOG 6293.10 Special Topics 201603\Volpe, Travis - TVolpe1\Final Project\GIS Python Project\Project Data\Data\Tracts_Wards2010_ratios.xlsx")
disindx_wards_ratios.to_excel(writer,)
writer.save()

#%%
#STEP 9
#This 'cell' takes the csv file with calaculate disimilarity index statistics for each ward
#   and join it the the wards layer

arcpy.env.overwriteOutput = True
arcpy.AddJoin_management('Ward__2002', 'OBJECTID', 'Tracts_Wards2010_DstatREADY.csv', 'OBJECTID', 'KEEP_ALL')


#%%
# FURTHER EXTENSIONS
# 1) Write python script to calculate the dissimilarity index and put it into excel file
# 2) Calculate different segregation indexes.
# 3) The basic dissimilarity index could be calculated for income. However, this would require extensive income data or at least data that divided the number of people in different income groups.
# 4) Calculate 10 year intervals for each census beginning in the 1950s when the DC began experiencing social unrest and segregation from the metro area
# 5) Further identify the segregated neighborhoods in each ward based on block level data
# 6) Calculate indexes for the whole metro area. The suburban and exurbs of DC are likely more segregated.
