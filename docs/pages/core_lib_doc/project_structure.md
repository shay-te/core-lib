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
    <a href="#core-lib-project-directory">core_lib</a> # Core-Lib Project Directory
    └───  <a href="#core-lib-main-code-directory">core_lib</a> # Core-Lib Main Code Directory
    |       └─── <a href="#config">config</a>
    |       |       └─── <a href="#corelibyaml">core_lib.yaml</a>
    |       └─── <a href="#data-layers">data_layers</a>
    |       |        └─── <a href="#data">data</a> # store all connector, definition, mapping to data sources
    |       |        |      └─── <a href="#db">db</a> # store database ORM entities
    |       |        |      |     └─── <a href="#migrations">migrations</a> # database migration scripts
    |       |        |      └─── <a href="#elastic">elastic</a> # store elastic search base classes
    |       |        |      └─── <a href="#mongo">mongo</a> # store mongo base classes
    |       |        └─── <a href="#data_access">data access</a> # expose API that uses data layer
    |       |        |	    └─── <a href="#user">user</a> # group user data access
    |       |        |	    |    └─── <a href="#user_data_accesspy">user_data_access.py</a>
    |       |        |	    |    └─── <a href="#user_list_data_accesspy">user_list_data_access.py</a>
    |       |        |	    └─── some_data_access.py 
    |       |        └─── <a href="#service">service</a> # expost the core-lib services
    |       |               └─── <a href="#user-1">user</a> # group user services
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

## Core-Lib Project Directory:
This root directory serves as the foundational structure for the Core-Lib project, encompassing all its project code and resources. It is a standard primary container for organizing and managing any Python project. Here, developers can find the core files and directories essential for building, configuring, and extending the functionality of the Core-Lib.

### Core-Lib Main Code Directory:
This subdirectory houses the main source code and modules of the Core-Lib, serving as the heart of the library. Developers will find key Python files and subdirectories containing the core functionalities and implementations that power the Core-Lib framework.

### Tests:
This directory contains the unit tests for the Core-Lib, allowing developers to verify the correctness and integrity of the library's functionalities. It includes test cases and configurations necessary for testing various components and features of the Core-Lib framework.

## Config:
This directory contains your Core-Lib configuration file crucial for configuring and customizing the Core-Lib to suit specific requirements.
### Core.lib.yaml:
A pivotal configuration file housing settings specific to the Core-Lib, facilitating easy customization and configuration of core functionalities.

## Data Layers:
This directory manages the core data layers of the library, responsible for handling data interactions and management.

### Data:
Within this subdirectory, various components related to different data sources and their interactions are organized.
#### db:
Stores components related to database interactions, including ORM entities and migration scripts necessary for schema modifications.
##### Migrations:
A repository for database migration scripts, crucial for managing schema changes and updates in database systems.

#### Elastic:
Contains base classes and utilities for interacting with Elasticsearch, facilitating efficient data retrieval and indexing operations.

#### Mongo:
Hosts base classes and utilities for MongoDB interactions, ensuring smooth handling of NoSQL database operations.


### Data_access:
This directory exposes APIs responsible for interacting with the data layer, promoting efficient data retrieval and manipulation.

#### User:
A dedicated module for user data access, providing methods for accessing and manipulating user-related data efficiently.
##### user_data_access.py:
Implements methods for accessing and manipulating user data, ensuring streamlined user-related operations.
##### user_list_data_access.py:
Facilitates batch operations and data retrieval for user lists, enhancing scalability and performance.

#### some_data_access.py:
An example module demonstrating data access for other entities or functionalities within the Core-Lib.

### Service:
This directory exposes essential services provided by the Core-Lib, encapsulating core functionalities and business logic.

#### User:
Contains service modules focused on user-related functionalities and operations.
##### user_service.py:
Implements user-related services such as user authentication, authorization, and profile management.
##### user_list_service.py:
Provides services for managing user lists and performing batch operations efficiently.

#### some_service.py:
Demonstrates service functionalities for other core components or functionalities.

## Jobs:
Hosts definitions for background tasks or scheduled operations, crucial for maintaining system integrity and performance.
### update_something_job.py:
Represents a job definition responsible for executing periodic updates or maintenance tasks within the system.
### another_job.py:
Another example job definition highlighting diverse functionalities or tasks handled by the Core-Lib.

## Client:
Contains client definitions facilitating interactions with external services, servers, or APIs.
### server_a_client.py:
Represents a client definition tailored for interacting with Server A, encapsulating communication protocols and data exchange mechanisms.
### another_client.py:
Another client definition catering to interactions with a different external service or system.

# app_core_lib.py:
This main Core-Lib file serves as the entry point for the entire library, orchestrating interactions between various components and providing essential functionalities to external modules or applications.
