---
id: project_structure
title: Project Structure
sidebar: core_lib_doc_sidebar
permalink: project_structure.html
folder: core_lib_doc
toc: false
---

# Core-Lib Folder Structure

**Note:** Generated `Core-Libs` will adopt the same folder structure. Following the same across all of your `Core-Libs` make it dive right into an existing project. 

<pre>
    <code>
    <a href="#core-lib-root-directory">core_lib</a> # Core-Lib Root Directory
    └───  <a href="#core-lib-main-directory">core_lib</a> # Core-Lib Main Directory
    |       |   └─── <a href="#config">config</a>
    |       |	   └─── <a href="#corelibyaml">core_lib.yaml</a>
    |       └─── <a href="#data-layers">data_layers</a>
    |       |        |   └─── <a href="#data">data</a> # store all connector, definition, mapping to data sources
    |       |        |          └─── <a href="#db">db</a> # store database ORM entities
    |       |        |          |     └─── <a href="#migrations">migrations</a> # database migration scripts
    |       |        |          └─── <a href="#elastic">elastic</a> # store elastic search base classes
    |       |        |          └─── <a href="#mongo">mongo</a> # store mongo base classes
    |       |        └─── <a href="#data_access">data access</a> # expose API that uses data layer
    |       |        |	    └─── <a href="#user">user</a> # grather user data access
    |       |        |	    |    └─── <a href="#user_data_accesspy">user_data_access.py</a>
    |       |        |	    |    └─── <a href="#user_list_data_accesspy">user_list_data_access.py</a>
    |       |        |	    └─── some_data_access.py 
    |       |        └─── <a href="#service">service</a> # expost the core-lib services
    |       |               └─── <a href="#user-1">user</a> # gather user services
    |       |               |    └─── <a href="#user_servicepy">user_service.py</a>
    |       |        	    |    └─── <a href="#user_list_servicepy">user_list_service.py</a>
    |       |        	    └─── <a href="#some_servicepy">some_service.py</a>
    |       └─── <a href="#jobs">jobs</a> # jobs definitions
    |       |	  └─── <a href="#update_something_jobpy">update_something_job.py</a>
    |       |	  └─── <a href="#another_jobpy">another_job.py</a>
    |       └─── <a href="#client">client</a> # client definitions
    |       |	  └─── <a href="#server_a_clientpy">server_a_client.py</a>
    |       |	  └─── <a href="#another_clientpy">another_client.py</a>
    |       └─── <a href="#app_core_libpy">app_core_lib.py</a> # Main Core-Lib file that glows the entire library 
    └─── <a href="#tests">tests</a> # Unit test the entire data_layers
     	 └─── config # config file for the tests
    </code>
</pre>

## Core-Lib Root Directory:
This root directory serves as the foundational structure for the Core-Lib, encompassing all its components and resources. It acts as the primary container for organizing and managing the various modules, configurations, and assets that constitute the Core-Lib framework. Here, developers can find the core files and directories essential for building, configuring, and extending the functionality of the Core-Lib.

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Core-Lib Main Directory:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This subdirectory houses the main source code and modules of the Core-Lib, serving as the heart of the library. Developers will find key Python files and subdirectories containing the core functionalities and implementations that power the Core-Lib framework.

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tests:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This directory contains the unit tests for the Core-Lib, allowing developers to verify the correctness and integrity of the library's functionalities. It includes test cases and configurations necessary for testing various components and features of the Core-Lib framework.

## Config:
This directory contains essential configuration files crucial for configuring and customizing the Core-Lib to suit specific requirements.
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Core.lib.yaml:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A pivotal configuration file housing settings specific to the Core-Lib, facilitating easy customization and configuration of core functionalities.

## Data Layers:
This directory manages the core data layers of the library, responsible for handling data interactions and management.

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Data:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Within this subdirectory, various components related to different data sources and their interactions are organized.
#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;db:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stores components related to database interactions, including ORM entities and migration scripts necessary for schema modifications.
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Migrations:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A repository for database migration scripts, crucial for managing schema changes and updates in database systems.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Elastic:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contains base classes and utilities for interacting with Elasticsearch, facilitating efficient data retrieval and indexing operations.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mongo:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hosts base classes and utilities for MongoDB interactions, ensuring smooth handling of NoSQL database operations.


### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Data_access:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This directory exposes APIs responsible for interacting with the data layer, promoting efficient data retrieval and manipulation.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A dedicated module for user data access, providing methods for accessing and manipulating user-related data efficiently.
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_data_access.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Implements methods for accessing and manipulating user data, ensuring streamlined user-related operations.
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_list_data_access.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Facilitates batch operations and data retrieval for user lists, enhancing scalability and performance.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;some_data_access.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;An example module demonstrating data access for other entities or functionalities within the Core-Lib.

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Service:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This directory exposes essential services provided by the Core-Lib, encapsulating core functionalities and business logic.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contains service modules focused on user-related functionalities and operations.
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_service.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Implements user-related services such as user authentication, authorization, and profile management.
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_list_service.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Provides services for managing user lists and performing batch operations efficiently.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;some_service.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demonstrates service functionalities for other core components or functionalities.

## Jobs:
Hosts definitions for background tasks or scheduled operations, crucial for maintaining system integrity and performance.
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;update_something_job.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Represents a job definition responsible for executing periodic updates or maintenance tasks within the system.
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;another_job.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Another example job definition highlighting diverse functionalities or tasks handled by the Core-Lib.

## Client:
Contains client definitions facilitating interactions with external services, servers, or APIs.
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;server_a_client.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Represents a client definition tailored for interacting with Server A, encapsulating communication protocols and data exchange mechanisms.
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;another_client.py:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Another client definition catering to interactions with a different external service or system.

# app_core_lib.py:
This main Core-Lib file serves as the entry point for the entire library, orchestrating interactions between various components and providing essential functionalities to external modules or applications.
