![](https://img.shields.io/pypi/v/foliantcontrib.meta.svg)

# Metadata for Foliant

This extension adds the `meta generate` command to Foliant, which generates the yaml-file with project metadata. It also allows to add other meta commands `meta <command>` which use the generated metadata.

## Installation

```bash
$ pip install foliantcontrib.meta
```

## Specifying metadata

Metadata for the *main section* (more on sections in **User's Guide** below) may be specified in the beginning of a Markdown-file using [YAML Front Matter](http://www.yaml.org/spec/1.2/spec.html#id2760395) format:

```yaml
---
id: MAIN_DOC
title: Description of the product
key: value
---
```

You may also use regular XML-like format with `meta` tag:

```html
<meta
    id="MAIN_DOC"
    title="Description of the product"
    key="value">
</meta>
```

> If `meta` tag is present, all Metadata from YAML Front Matter is ignored.


## `meta generate` command

### Usage

To generate meta file run the `meta generate` command:

```bash
$ foliant meta generate
```

Metadata for the document will appear in the `meta.yml` file.

### Config

Meta generate command has just one option right now. It is specified under `meta` section in config:

```yaml
meta:
    filename: meta.yml
```

`filename`
:   name of the YAML-file with generated project metadata.

# User's guide

Metadata allows you to specific properties to your documents, which won't be visible directly to the end-user. These properties may be:

- the document author's name;
- Jira ticket id;
- date of last revision;
- or anything else, there is not limitation.

This module is required for metadata to work in your projects. But it doesn't care about most of the fields and their values. The only exception being the `id` field. See **Special fields** section.

# Sections

You can specify metadata for a whole chapter and for it's portions, which are called *sections*. Section is a fragment of the document from one heading to another one of the same level of higher.

Metadata, specified at the beginning of the document (before the first heading), is applied to the whole Markdown document. We call it the *main section* of the chapter.

> Note that you can specify metadata for the main section either in YAML Front Matter format, or with `meta` tag.

If you specify metadata after the heading of some level, it will be applied to all content inside this heading, including all other nested headings. See the illustration below.

![](img/pic1.png)

# Special fields

Right now there's only one field that is treated specially: the `id` field.

If specified, it will used as identificator of the section. Note that IDs must be unique within the whole project.

If `id` field is omited — the section will get auto generated id based on:

- chapter filename for main section,
- title for general sections.

# Additional info

Metadata works only for files, mentioned in the `chapters` section in foliant.yml. All other files in `src` dir are ignored.

When using [includes](https://foliant-docs.github.io/docs/preprocessors/includes/), all metadata from the included content is removed.
