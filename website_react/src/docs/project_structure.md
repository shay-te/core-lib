Code-Lib recommended Folder Structure:

 ``` 
This is how code of Core-Lib is mapped internally. 
Core-Lib can be connected to a network of Core-Lib that can 
easly expand by extending each other pipe-line (Look at the code for combine example)
 ```



```
core_lib // root folder of our library
└─── data_layers
|    └─── data // store all connector, definition, mapping to data sources
|    │    └─── db // store database ORM entities
|    │       └─── migrations // data base migration scripts
|    │    └─── elastic // store elastice search base classes
|    │    // etc..
|    └─── data_access // expose API that uses data layer
|	 |    └─── user // grather user data access
|	 |    	   └─── user_data_access.py
|	 |    	   └─── user_list_data_access.py
|	 |    └─── some_data_access.py 
|    └─── service // expost the core-lib services
|	 |    └─── user // gather user services
|	 |    	   └─── user_service.py
|	 |    	   └─── user_list_service.py
|	 |    └─── some_service.py 
|    app_core_lib.py //The file that glow the entire up togther 
└─── job // jobs defenitions
tests // Unit test the enttire data_layers 
```
