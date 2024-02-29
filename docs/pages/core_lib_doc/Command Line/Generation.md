---
id: generation
title: Generation
sidebar: core_lib_doc_sidebar
permalink: generation.html
folder: core_lib_doc
toc: false
---

`core_lib_main` is the single gateway to interact with `Core-Lib` using the command line.  
It offers the following tools:

- Generating `Core-Lib` from YAML will create a `Core-Lib` folder with your `Core-Lib` inside.
- Run Migration, `Alembic` upgrade, or downgrade for migrations.
- List Migrations created until now.


> Please don't change the structure of the Yaml data as this file is responsible for generating the `Core-Lib`, you can add or remove any Entity, DataAccess or any other items inside other layers.

## Generate a new Core-Lib from the YAML file 

### Command

```python
core_lib -g ExampleCoreLib.yaml
```

Run this command where the Yaml file is located or re-locate the file to a location where you want to create the `Core-Lib`.

### Outcome

A folder by the `Core-Lib` name will be created and inside the folder will be your `Core-Lib`!

Now that you have the `Core-Lib` you can initialize it and use it directly or integrate it with your current application.

> Please read the documents to understand what each file does and understand `Core-Lib` more throughly.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/migrations.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/cache.html">Next >></a></button>
</div>