---
id: article_layers
title: Data Layers
sidebar_label: Data Layers
---

Data is moving and transforming in a single direction. from the physical disk until it meets the user's screen.
braking down the data flow into layers with an agreement up front on a set of rules and responsibilities may help us manage our code more easily.


####  “Complexity is the enemy of execution”. Tony Robbins

To make our application more resilient is to make it more simple to use.   
by simply handling fewer responsibilities. 
Simply means less complexity in our code.

The best way to solve this is by delegating responsibilities into different categories.
  

### Layer Rules:

To make sure that the responsibilities of each layer are done only by the designated layer. 
We will decide upfront of some rules:


[!POINT] When writing any type of `data-layer` try to put on the hat of one that will use your data-layer APIs.  

1. Data layer will get data internally only from layers beside or below it.    
2. Each layer will be agnostic and will handle error/create custom exceptions/logging/etc.. internally   
   To make our layers independent and portable


## Data Layer:
<table><tr>
        <td><b>Input</b></td>
        <td>Data Sources/Configuration</td>
    </tr><tr>
        <td><b>Expose</b></td>
        <td>ORM Entities, Clients, etc..</td>
    </tr><tr>
        <td><b>Responsibilities</b></td>
        <td>Define connectors, clients, Map data, Migration, ORM entities, local/remote files, etc..</td>
</tr></table>


## Data-Access Layer:

<table><tr>
        <td><b>Input</b></td>
        <td>Data Layer</td>
    </tr><tr>
        <td><b>Expose</b></td>
        <td>Data as API calls that will be used by the layer above it.</td>
    </tr><tr>
        <td><b>Responsibilities</b></td>
        <td>
            1. Describe Internal API  
        </td>
    </tr><tr><td></td><td>2. Data Optimization</td>
    </tr><tr><td></td><td>3. Caching</td>
</tr></table>


data-access layers are the way we access the data of our application. thus layers are the single source of truth for data fetching.

here we will optimize queries, cache data, work with multiple data sources and more.

this layer single responsibility is to fetch data from the previous layer and expose them as APIs of the application.

* using native queries/ORM is less important for the data flow as long that we keep layer rule number 1.

## Service Layer:

<table><tr>
        <td><b>Input</b></td>
        <td>Data-Access/Services Layer</td>
    </tr><tr>
        <td><b>Expose</b></td>
        <td>Data after business logic.</td>
    </tr><tr>
        <td><b>Responsibilities</b></td>
        <td>
            1. Describe Public  
        </td>
    </tr><tr><td></td><td>2. Bossiness Logic</td>
    </tr><tr><td></td><td>3. Expose a single data type</td>
    </tr><tr><td></td><td>4. Caching</td>
</tr></table>

### Application layer:

<table><tr>
        <td><b>Input</b></td>
        <td>Services Layer</td>
    </tr><tr>
        <td><b>Expose</b></td>
        <td>Single interface of our library.</td>
    </tr><tr>
        <td><b>Responsibilities</b></td>
        <td>
            1. Describe Public  
        </td>
    </tr><tr><td></td><td>2. Bossiness Logic</td>
    </tr><tr><td></td><td>3. Expose a single data type</td>
    </tr><tr><td></td><td>4. Caching</td>
</tr></table>


here we will have custom implementation for each interface (web/mobile/pager/etc..)
And this layer we will handle our users and session

## WEB layer:
receive: data using the application layer
expose: rest API

each layer act as an interface to the layer below it.


