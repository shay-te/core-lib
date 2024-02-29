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
    |       |       └─── <a href="#core-lib-yaml">core_lib.yaml</a>
    |       └─── <a href="#data-layers">data_layers</a>
    |       |        └─── <a href="#data">data</a> # store all connector, definition, mapping to data sources
    |       |        |      └─── <a href="#db">db</a> # store database ORM entities
    |       |        |      |     └─── <a href="#migrations">migrations</a> # database migration scripts
    |       |        |      └─── <a href="#elastic">elastic</a> # store elastic search base classes
    |       |        |      └─── <a href="#mongo">mongo</a> # store mongo base classes
    |       |        └─── <a href="#data_access">data access</a> # expose API that uses data layer
    |       |        |	    └─── <a href="#user">user</a> # group user data access
    |       |        |	    |    └─── <a href="#user_data_access-py">user_data_access.py</a>
    |       |        |	    |    └─── <a href="#user_list_data_access-py">user_list_data_access.py</a>
    |       |        |	    └─── some_data_access.py 
    |       |        └─── <a href="#service">service</a> # expost the core-lib services
    |       |               └─── <a href="#user-1">user</a> # group user services
    |       |               |    └─── <a href="#user_service-py">user_service.py</a>
    |       |        	    |    └─── <a href="#user_list_service-py">user_list_service.py</a>
    |       |        	    └─── <a href="#some_service-py">some_service.py</a>
    |       └─── <a href="#jobs">jobs</a> # jobs definitions
    |       |	  └─── <a href="#update_something_job-py">update_something_job.py</a>
    |       |	  └─── <a href="#another_job-py">another_job.py</a>
    |       └─── <a href="#client">client</a> # client definitions
    |       |	  └─── <a href="#server_a_client-py">server_a_client.py</a>
    |       |	  └─── <a href="#another_client-py">another_client.py</a>
    |       └─── <a href="#app_core_libpy">app_core_lib.py</a> # Main Core-Lib file that glows the entire library 
    └─── <a href="#tests">tests</a> # Unit test the entire data_layers
     	 └─── config # config file for the tests
    </code>
</pre>

## Core-Lib Project Directory:
This root directory serves as the foundational structure for the `Core-lib` project, encompassing all its project code and resources. It is a standard way to manage any Python project. Here, developers can find the core files and directories essential for building, configuring, and extending the functionality of the `Core-lib`.

- <h3>Core-Lib Main Code Directory:</h3>
This directory contains the main source code and modules of `Core-lib`, serving as the heart of the library. Developers will find key Python files and subdirectories containing the core functionalities and implementations that power the `Core-lib` framework.

- <h3>Tests:</h3>
This directory contains the unit tests for `Core-lib`, allowing developers to verify the correctness and integrity of the library's functionalities. It includes test cases and configurations necessary for testing various components and features of the `Core-lib` framework.

## Config:
This directory contains your `Core-lib` configuration file crucial for configuring and customizing `Core-lib` to suit specific requirements.

- <h3>Core.lib.yaml:</h3>
A main configuration file containing settings specific to `Core-lib`, facilitating easy customization and configuration of core functionalities.

## Data Layers:
This directory manages the core data layers of the library, responsible for handling data interactions and management.

### Data:
Within the `Data Layers` directory, this serves as a subdirectory where various components related to different data sources and their interactions are organized.
- <h4>db:</h4>
Stores components related to database interactions, including `ORM entities` and `migration scripts` necessary for schema modifications.
    - <h5>Migrations:</h5> A repository for database `migration scripts`, crucial for managing schema changes and updates in database systems.

- <h4>Elastic:</h4>
Contains `base classes` and `utilities` for interacting with `Elasticsearch`, facilitating efficient data retrieval and indexing operations.

- <h4>Mongo:</h4>
Hosts `base classes` and `utilities` for `MongoDB` interactions, ensuring smooth handling of `NoSQL` database operations.


### Data_access:
Within the `Data Layers` directory, this directory exposes `APIs` responsible for interacting with the data layer, promoting efficient data retrieval and manipulation.

- <h4>User:</h4>
A dedicated module for user data access, providing methods for accessing and manipulating user-related data efficiently.
    - <h5>user_data_access.py:</h5> Implements methods for accessing and manipulating user data, ensuring streamlined user-related operations.
    - <h5>user_list_data_access.py:</h5> Facilitates batch operations and data retrieval for user lists, enhancing scalability and performance.

- <h4>some_data_access.py:</h4>
An example module demonstrating data access for other entities or functionalities within the `Core-lib`.

### Service:
This directory exposes essential services provided by the `Core-lib`, encapsulating core functionalities and business logic.

- <h4>User:</h4>
Contains service modules focused on user-related functionalities and operations.
    - <h5>user_service.py:</h5> Implements user-related services such as user authentication, authorization, and profile management.
    - <h5>user_list_service.py:</h5> Provides services for managing user lists and performing batch operations efficiently.

- <h4>some_service.py:</h4>
Demonstrates service functionalities for other core components or functionalities.

## Jobs:
Hosts definitions for background tasks or scheduled operations, crucial for maintaining system integrity and performance.
- <h3>update_something_job.py:</h3>
Represents a job definition responsible for executing periodic updates or maintenance tasks within the system.
- <h3>another_job.py:</h3>
Another example job definition highlighting diverse functionalities or tasks handled by the `Core-lib`.

## Client:
Contains client definitions facilitating interactions with `external services`, `servers`, or `APIs`.
- <h3>server_a_client.py:</h3>
Represents a client definition tailored for interacting with Server A, encapsulating communication protocols and data exchange mechanisms.
- <h3>another_client.py:</h3>
Another client definition catering to interactions with a different external service or system.

# app_core_lib.py:
This main `Core-lib` file serves as the entry point for the entire library, orchestrating interactions between various components and providing essential functionalities to external modules or applications.
