---
id: generation
title: Generation
sidebar: core_lib_doc_sidebar
permalink: generation.html
folder: core_lib_doc
toc: false
---

Setting up a new `CoreLib` by hand means creating ~20 files in the right folders with the right inheritance — easy to get wrong and tedious to repeat. The `core_lib generate` command takes a YAML description of your services and scaffolds the entire project structure: folders, base classes, entities, data accesses, services, and config.

> **Where it fits:** Project setup. The generator creates the folders and starter classes for the six-layer structure; after generation, you fill in your domain logic.

> Don't change the YAML's top-level structure — `core_lib generate` reads specific keys. You can freely add or remove entities, data accesses, and other items inside the layers.

## Generate from a YAML file

```bash
core_lib generate --yaml ExampleCoreLib.yaml
```

Run this from the directory where the YAML file lives. If you omit `--yaml`, an interactive prompt walks you through creating the YAML first.

The command creates a folder named after your `CoreLib` containing a full project skeleton: entities, data access classes, services, config, and the wiring class. See [Project Structure](/project_structure.html) for what each folder is for.

Example output shape:

```text
example_core_lib/
├── config/
├── data_layers/
│   ├── data/
│   ├── data_access/
│   └── service/
├── client/
├── jobs/
└── example_core_lib.py
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/migrations.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/cache.html">Next</a></button>
</div>
