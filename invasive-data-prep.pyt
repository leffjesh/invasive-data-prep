'''
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
import arcpy, uuid, time

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "arcgis-toolbox-uniqueIDgenerator"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [UUIDUpdater, iMapDataPrep]


class UUIDUpdater(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "UUIDUpdater"
        self.description = "Tool to add UUIDs to specified attribute for all records.  Records with attribute already defined will be skipped.  The specified attribute must be a text attribute."
        self.canRunInBackground = False

    def getParameterInfo(self):
        # First parameter
	    param0 = arcpy.Parameter(
	        displayName="Input Feature",
	        name="in_feature",
	        datatype="GPFeatureLayer",
	        parameterType="Required",
	        direction="Input")
	
	    # Second parameter
	    param1 = arcpy.Parameter(
	        displayName="UUID Field",
	        name="uuid_field",
	        datatype="Field",
	        parameterType="Required",
	        direction="Input")
	
	    param1.value = "sourceUniqueID"
	
	    params = [param0, param1]
	
	    return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        inFeatures      = parameters[0].value
    	attribute = parameters[1].value
        
        rows = arcpy.UpdateCursor(inFeatures)
        for row in rows:
            if row.isNull(attribute) or row.getValue(attribute) == " ":
                uuid_val = str(uuid.uuid4()) 
                row.setValue(attribute, uuid_val)
            rows.updateRow(row)
        return


class iMapDataPrep(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "iMapDataPrep"
        self.description = "Automates some of the steps required to prep weed observation point data for inclusion in iMap dataset. "+\
            " Counties layer must only be for state in question and must utilize desired projection for new dataset. " + \
            " Tasks performed: - clip to 1/2 mile buffer of state, reproject to state format, populate county field, "+\
            "modify data by updating synonyms table to update names to new nomenclature, "+\
            "populate state species ID, scientific, common_names, (possible future work would be to populate observer IDs using a list of synonyms for an observer)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Bulk Upload Layer",
            name="bulk_layer_in",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Scientific Name",
            name="Scientific",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="state_counties",
            name="state_counties",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param3 = arcpy.Parameter(
            displayName="State Species List Table",
            name="state_ids",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input")
        
        param4 = arcpy.Parameter(
            displayName="Synonym Table",
            name="synonyms",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input")
        
        param5 = arcpy.Parameter(
            displayName="Output Workspace",
            name="bulk_layer_out",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        
        param5.filter.list = ["Local Database"]
        param0.filter.list = ["Point"]
        param2.filter.list = ["Polygon"]
        params = [param0, param1, param2, param3,param4, param5]
    
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        out_featureclass= "bulk_out" + str(int(time.time()))
        
        
        bulk_in = parameters[0].value
        bulk_in_sci_field = parameters[1].value
        state_counties = parameters[2].value
        species_table = parameters[3].value
        synonym_table = parameters[4].value
        bulk_out = parameters[5].value
        
        #required for in_memory 
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = bulk_out
        
        spatial_ref = arcpy.Describe(state_counties).spatialReference
        
        #=======================================================================
        # #re project
        #=======================================================================
        arcpy.Project_management (bulk_in, "bulk_in_reprojected", spatial_ref)
        
        #=======================================================================
        # #clip data
        #=======================================================================
        arcpy.Dissolve_management(state_counties, "in_memory/state_boundary", "", "", "SINGLE_PART", "DISSOLVE_LINES")
        arcpy.MakeFeatureLayer_management("bulk_in_reprojected", "in_lyr")
        arcpy.MakeFeatureLayer_management("in_memory/state_boundary", "boundary")
        arcpy.SelectLayerByLocation_management("in_lyr", "within_a_distance", "boundary", "1320 Feet")
        
        #=======================================================================
        # #add xy
        #=======================================================================
        fields = [f.name for f in arcpy.ListFields("in_lyr")]
        if not "origx" in fields:
            arcpy.AddField_management("in_lyr", "origx", "DOUBLE")
        if not "origy" in fields:
            arcpy.AddField_management("in_lyr", "origy", "DOUBLE")
        arcpy.CalculateField_management("in_lyr", "origx", 
                                        "!SHAPE.CENTROID.X!",
                                        "PYTHON_9.3")
        arcpy.CalculateField_management("in_lyr", "origy", 
                                        "!SHAPE.CENTROID.Y!",
                                        "PYTHON_9.3")
        #=======================================================================
        # #add county
        #=======================================================================
        if not "County" in fields:
            arcpy.AddField_management("in_lyr", "County", "TEXT")
  
        arcpy.SpatialJoin_analysis("in_lyr", state_counties, "in_memory/in_lyr_withCounty","#","#","","within")
        arcpy.CalculateField_management("in_memory/in_lyr_withCounty","County","!altName!","PYTHON_9.3")

        arcpy.CopyFeatures_management("in_memory/in_lyr_withCounty", "in_memory/bulk_out")
        
        arcpy.Delete_management("in_memory/in_lyr_withCounty")
        arcpy.Delete_management("in_memory/state_boundary")
        
        # Use ListFields to get a list of field objects
        fieldObjList = arcpy.ListFields(state_counties)
        fieldNameList = []
     
        for field in fieldObjList:
            if not field.required:
                fieldNameList.append(field.name)
        arcpy.DeleteField_management("in_memory/bulk_out", fieldNameList)
        
        #=======================================================================
        # add species ID, commonname, and scientificname
        #=======================================================================
        arcpy.MakeTableView_management(species_table,"species_table")
        arcpy.MakeTableView_management(synonym_table,"synonym_table")
        arcpy.MakeFeatureLayer_management("in_memory/bulk_out","bulk_out_fl")
        
        #=======================================================================
        # #edit bulk_out_fl to remove extra white space in scientific field, update species names using synonyms table
        #=======================================================================
        
        #create data structure with weed informations
        cursor = arcpy.SearchCursor("synonym_table")
        weeds = {}
        for row in cursor:
            weeds[row.getValue("synonym")] = "NULL"
            weeds[row.getValue("stateSpeciesID")] = row.getValue("synonym")
        
        del cursor, row
  
        cursor = arcpy.SearchCursor("species_table")
        for row in cursor:
            if row.getValue("stateSpeciesID") in weeds:
                field = weeds[row.getValue("stateSpeciesID")]
                val = row.state_scientific_name
                weeds[ field  ] = val

        #process records and update nomenclature and remove trailing and leading whitespace
        records = arcpy.UpdateCursor("bulk_out_fl")
        for record in records:
            sci_name_given = record.getValue(bulk_in_sci_field)
            sci_name_given = sci_name_given.strip()
            
            if sci_name_given in weeds and weeds[sci_name_given] != "NULL":
                record.setValue(bulk_in_sci_field, weeds[sci_name_given] )
            else:
                #this fixes trailing and leading whitespace
                record.setValue(bulk_in_sci_field, sci_name_given )
            records.updateRow(record)

        del record, records
        
        #add new fields for species info
        new_fields = [["stateSpeciesID",15],["state_scientific_name",255], ["stateCommonName",255] ]
        existing_fields = [f.name for f in arcpy.ListFields("bulk_out_fl")]
        
        for field in new_fields:
            if not field[0] in existing_fields:
                arcpy.AddField_management("bulk_out_fl", field[0], "TEXT", field[1])
        
        #add species fields from specified table view
        arcpy.AddJoin_management("bulk_out_fl", bulk_in_sci_field, "species_table", "state_scientific_name", "KEEP_COMMON")
        
        #copy info from join into permanent fields
        desc = arcpy.Describe("species_table")
        for field in new_fields:
            arcpy.CalculateField_management("bulk_out_fl",field[0],"!"+desc.name+"."+field[0]+"!","PYTHON_9.3")

        #remove join so that we don't export extra fields
        arcpy.RemoveJoin_management("bulk_out_fl")
        
        #write to disk
        arcpy.CopyFeatures_management("bulk_out_fl", out_featureclass)
        
        arcpy.Delete_management("in_memory/bulk_out")
        
        return
        
if __name__ == '__main__':
    # This is used for debugging. Using this separated structure makes it much easier to debug using standard Python development tools.

    tasks = iMapDataPrep()
    params = tasks.getParameterInfo()
    params[0].value = 'C:/temp3/points.shp'
    params[1].value = 'scientific'
    params[2].value = 'C:/temp3/orcnty24.shp'
    params[3].value = 'C:/temp3/state_species_list_20140107.csv'
    params[4].value = 'C:/temp3/synonyms.csv'
    params[5].value = 'C:/temp3/New File Geodatabase.gdb'
    
    tasks.execute(params, None)

    print(tasks.label)