---
id: advantages
title: Advantages
sidebar_label: Advantages
---

# Advantages



#### It can be deployed anywhere.

Running/Debuging `Core-Lib` is simple as running `__main__` function inside the `IDE`.
`Core-Lib` class instance can be placed after any interface such as `UnitTest`, ` WEB`, `Microservice`, And more.

#### Unit test the entire product.

All of the `Core-Lib` API's are executed as plain python functions that can be called from Unit-tests. 


#### Write code that matters.

`Core-Lib` delegates operations that frequently repeat into tools and decorators such as  `Cache`, `Transform Data`, `RuleValidator`, etc. Leaving you to focus on the problem at hand.

#### Short learning curve.

`Core-Lib` provides out-of-the-box a tiny subset of simple tools that are easy to master. 

#### Risk management

`Core-Lib` dose not delegate third-party dependencies. Relying on multiple dependencies rather than one add risk management when main dependence becomes obsolete. 


#### Shared knowledge

Architecture, code structure, state of mind, approach, knowledge, experience, and problem resolution will be almost the same from one `Core-Lib` to another.


#### Divide and Conquer

`Core-Lib` makes it easy to break a product into other `Core-Libs`,  `Services` and ` Data-Layers`. Creating smaller units that are easier to seperate, read, develop, pinpoint a problem, and test.

#### Easy to scale, And Longevity

`Core-Lib` embraces the `Onion Architecture` for data flow across libraries. Make it easy to rewire and expend logic across data layers (`Core-Lib`/ `Services`/`DataAccess`.), preventing busy/complex code and encouraging code reuse.

#### Configuration on adtroied 

`Core-Lib` uses [hydra](https://hydra.cc/) to discover other `Core-Libs` configurations. And instantiate `Core-Lib` and its dependencies from config.

