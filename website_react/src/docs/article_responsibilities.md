---
id: article_responsibilities
title: Responsibilities
sidebar_label: Responsibilities
---


Data is stored, processed and transformed into the application that meets the user on his personal computer screen. where the data is displayed and organised in a more human way.   

Transforming data from its RAW state (Databases, S3, etc..) into the user interface.     
It’s not rocket science complex. but it is a complex task.   

The nature of the task require from us to handle framework, libraries, business logic, different types of storage and data sources, session, security, status codes, classes, variables, error handling and more.    

The table below illustrate the list of responsibilities we will probably encounter in singe function or file.    
 
|Responsibility|Descriptions|Code dependencies|
|---|---|---|
|Load resources|Load photos and other resources.|Classes/variables.
|Load data|Load data from versus sources.|Classes/variables.
|External libraries|Dependencies for our application.|Classes/variables/constants
|Transform data|Business logic and processing.|Classes/variables.
|Caching|Improve the performance of our product.|Classes/variables.
|Business logic|Our product code.|Classes/variables/constants/logic
|Web framework|Web interface with the outer worlds|Classes/variables/constants/session/status codes/etc..

(not all of the requirements listed above will be used by our application, over time we may add/change responsibilities and capabilities on a small time frame.

##### “Indeed, the ratio of time spent reading versus writing is well over 10 to 1. We are constantly reading old code as part of the effort to write new code. ...[Therefore,] making it easy to read makes it easier to write.” Robert C. Martin.
