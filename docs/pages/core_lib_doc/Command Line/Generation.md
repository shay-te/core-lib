---
id: generation
title: Generation
sidebar: core_lib_doc_sidebar
permalink: generation.html
folder: core_lib_doc
toc: false
---

Setting up a new `CoreLib` by hand means creating ~20 files in the right folders with the right inheritance — easy to get wrong and tedious to repeat. The `core_lib generate` command takes a YAML description of your services and scaffolds the entire project structure: folders, base classes, entities, data accesses, services, and config.

> Don't change the YAML's top-level structure — `core_lib generate` reads specific keys. You can freely add or remove entities, data accesses, and other items inside the layers.

## Generate a new Core-Lib from the YAML file 

### Command

```bash
core_lib generate --yaml ExampleCoreLib.yaml
```

Run this command where the YAML file is located. If `--yaml` is omitted, an interactive prompt will guide you through creating the YAML file first.

### Outcome

A folder by the `Core-Lib` name will be created and inside the folder will be your `Core-Lib`!

Now that you have the `Core-Lib` you can initialize it and use it directly or integrate it with your current application.

> Please read the documents to understand what each file does and understand `Core-Lib` more thoroughly.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/migrations.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/cache.html">Next >></a></button>
</div>