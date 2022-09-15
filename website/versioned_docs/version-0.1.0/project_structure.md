---
id: project_structure
title: Project Structure
sidebar_label: Project Structure
---

## Core-Lib Folder Structure

**Note:** Generated `Core-Libs` will adopt the same folder structure, it is recommended to follow the same across all of your `Core-Libs`

```
core_lib # root folder of our library
└─── data_layers
|    └─── data # store all connector, definition, mapping to data sources
|    │    └─── db # store database ORM entities
|    │       └─── migrations # database migration scripts
|    │    └─── elastic # store elastic search base classes
|    │    # etc..
|    └─── data_access # expose API that uses data layer
|	 |    └─── user # grather user data access
|	 |    	   └─── user_data_access.py
|	 |    	   └─── user_list_data_access.py
|	 |    └─── some_data_access.py 
|    └─── service # expost the core-lib services
|	 |    └─── user # gather user services
|	 |    	   └─── user_service.py
|	 |    	   └─── user_list_service.py
|	 |    └─── some_service.py 
|    app_core_lib.py # The file that glows the entire together 
└─── job # jobs definitions
tests # Unit test the entire data_layers 
```

