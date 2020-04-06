[![](https://img.shields.io/pypi/v/foliantcontrib.meta.svg)](https://pypi.org/project/foliantcontrib.meta/)  [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.meta.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.meta)

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
- or anything else, there is no limitation.

This module is required for metadata to work in your projects. But it doesn't care about most of the fields and their values. The only exception being the `id` field. See **Special fields** section.

## Sections

You can specify metadata for a whole chapter and for it's portions, which are called *sections*. Section is a fragment of the document from one heading to another one of the same level of higher.

Metadata specified at the beginning of the document (before the first heading) is applied to the whole Markdown document. We call it the *main section* of the chapter.

> Note that you can specify metadata for the main section either in YAML Front Matter format, or with `meta` tag.

If you specify metadata after the heading of some level, it will be applied to all content inside this heading, including the nested headings. See the illustration below.

![](https://raw.githubusercontent.com/foliant-docs/foliantcontrib.meta/master/img/pic1.png)

## Special fields

Right now there's only one field that is treated specially: the `id` field.

If specified, it will be used as identifier of the section. Note that IDs must be unique within the project.

If `id` field is omitted — the section will get auto generated id based on:

- chapter filename for main section,
- title for general sections.

## Additional info

Metadata works only for files, mentioned in the `chapters` section in foliant.yml. All other files in `src` dir are ignored.

When using [includes](https://foliant-docs.github.io/docs/preprocessors/includes/), all metadata from the included content is removed.

# Developer's guide

You can use the powers of metadata in  your preprocessors, backends and other tools. You can define fields with special meaning for your tools and process sections based on these fields.

## Getting metadata

Typical way to work with metadata is to run the `load_meta` function from the `foliant.meta.generate` module.

**load_meta(chapters: list, md_root: str or PosixPath = 'src') -> Meta**

This function collects metadata and returns a `Meta` object, which gives access to all sections and meta-fields in the project.

The required parameter is `chapters` — list of chaters loaded from foliant.yml

```python
>>> from foliant.meta.generate import load_meta
>>> meta = load_meta(['index.md'])
```

You can also specify the `md_root` parameter. If your tool is a CLI extension, `md_root` should point to the project's `src` dir. But if you are building a preprocessor or a backend, you would probably want to point it to the `__folianttmp__` dir with the current state of the sources.

## The Meta class

Meta class holds all metadata and offers few handy methods to work with it.

**load_meta_from_file(filename: str or PosixPath)**

This method allows you to load meta into the Meta class instance from previously generated yaml-file. Use it only with empty Meta class:

```python
>>> from foliant.meta.classes import Meta
>>> meta = Meta()
>>> meta.load_meta_from_file('meta.yml')
```

**iter_sections()**

This method returns an iterator which yields project's meta-sections (`Section` objects) in the proper order from the first chapter to the last one.

**get_chapter(self, filename: str or PosixPath) -> Chapter**

Get chapter (`Chapter` object) by its path. `filename` should be path to chapter relative to the Project dir (or absolute path).

**get_by_id(self, id_: str) -> Section**

Get section (`Section` object) by its id.

**chapters**

A property which holds the list of chapters (`Chapter` objects).

## The Chapter class

`Chapter` class represents a project's chapter. It has several important methods which may be useful for working with metadata.

**iter_sections()**

This method returns an iterator which yields chapter's meta-sections (`Section` objects) in the proper order from the first chapter to the last one.

**get_section_by_offset(offset: int) -> Section:**

This method allows you to get section (`Section` object) by just pointing to a place in text. Pointing is performed by specifying offset from the beginning of the file in `offset` parameter.

*important properties*

**main_section**

A property which holds the main section of the chapter.

**name**

Chapter's name.

**filename**

Chapter's filename.

## The Section class

`Section` represents a meta section.

**iter_children()**

This method returns an iterator which yields the section's child sections (`Section` objects) in the proper order.

**get_source(self, without_meta=True) -> str**

Returns section's source. If `without_meta` is `True`, all meta tags are cut out from the text.

**is_main(self) -> bool**

Determine whether the section is main or not.

*important properties*


**id**

Holds section's ID.

**title**

Section's title.

**chapter**

Holds reference to section's chapter.

**children**

Holds list of section's children in proper order.

**data**

Holds a dictionary with fields and their values, defined in the `<meta>` tag (or YAML front matter if it is a main section).

**level**

Section's level. Main section has level `0`, section, defined inside the `###` heading will have level `3`.

**start** and **end**

Section's offsets from the beginning of the chapter.

**filename**

Holds reference to section's chapter's filename for easy access.
