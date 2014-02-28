invasive-data-prep
==================
Requirements:

You must have ArcGIS installed in order to use this. Developed with ArcGIS 10.1 SP1 install, but probably works on new versions.

Background:

iMap is a tool used by some US and Canadian state/province entities to manage and share invasive species data (all taxa).  The process of prepping data from various partners and entities within a state has fallen to the state's iMap data administrator.  This task often results in similar data management challenges, of which this tool seeks to automate some.   Currently, it only supports processing of point observation data.   Coding contributions are welcome.  Future work is detailed below. This tool is not designed to be "bulletproof" or support use by casual ArcGIS users.

Issues?

Github allows for "issues" to be submitted on any project, so use that if you have any trouble so that there is a record for other to peruse.

Setup:

1. Download the .pyt file. 
2. In ArcGIS right-click in ArcToolbox window and select "Add Toolbox". Then navigate to the *.pyt file included in this repository and you will have access to this tool.

If there is a red X icon on the downloaded file, something is wrong.  Be sure to download the raw .pyt file.

Upon successfully loading the tool, you will notice two different tools.  

UUID

The UUIDgenerator is mostly for data contributers so that they can generate permanent unique IDs for their submissions.  This helps submitters or data consolidators to extract only the newest data.  One way to do this would be to join an old data set to a new dataset based on this uuid field.  then select all the records where the join did not result in new attributes (null).  

iMapDataPrep

This tools automates some of the steps required to prep weed observation point data for inclusion in iMap dataset.

Paramaters:

-Bulk upload layer - points from data contributer

-Scientific name - the field in the bulk upload layer that contains the scientific names of the weeds

-Counties Layer - must only be for state in question and must utilize desired projection for new dataset. 

-state species list - any table (or imported csv/etc) can be used.  see example provided for format

-synonym table - see example provided

-output workspace - must be file or personal geodatabase.  this is used to create the output layer.  (can we all just stop using shapefiles please).



Tasks performed: 
  
  -clip to 1/2 mile buffer of state
  
  -reproject to state format
  
  -populate county field
  
  -adds origx, origy fields and populates them using the new projection from the county layer
  
  -stardardize nomenclature using synonyms table
  
  -populate state species ID, scientific, common_names
  
  
Future ideas (iMapDataPrep) - 
  -populate observer IDs using a list of names used by an observer
  
  -support polygons
  
  
Future work (general)-
  ?
  
  
  
  
