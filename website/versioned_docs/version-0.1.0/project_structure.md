---
id: project_structure
title: Project Structure
sidebar_label: Project Structure
---

## Core-Lib Folder Structure

**Note:** Generated `Core-Libs` will adopt the same folder structure. Following the same across all of your `Core-Libs` make it dive right into an existing project. 

```
core_lib
└─── core_lib # root folder of our library
| 	 └─── config
|	 	 |    └─── core_lib.yaml
|		 └─── data_layers
|		 |    └─── data # store all connector, definition, mapping to data sources
|		 |    │    └─── db # store database ORM entities
|		 |    │    |    └─── migrations # database migration scripts
|		 |    │    └─── elastic # store elastic search base classes
|		 |    │    └─── mongo # store mongo base classes
|		 |    └─── data_access # expose API that uses data layer
|		 |	  |    └─── user # grather user data access
|		 |	  |    |    └─── user_data_access.py
|		 |	  |    |    └─── user_list_data_access.py
|		 |	  |    └─── some_data_access.py 
|		 |    └─── service # expost the core-lib services
|		 |	  |    └─── user # gather user services
|		 |	  |    |    └─── user_service.py
|		 |	  |    |    └─── user_list_service.py
|		 |	  |    └─── some_service.py 
|		 └─── job # jobs definitions
|		 |	  |    └─── update_something_job.py
|		 |	  |    └─── another_job.py
|		 └─── client # client definitions
|		 |	  |    └─── server_a_client.py
|		 |	  |    └─── another_client.py
|		 └─── app_core_lib.py # Main Core-Lib file that glows the entire library 
└─── tests # Unit test the entire data_layers
| 	 └─── config # config file for the tests
```

