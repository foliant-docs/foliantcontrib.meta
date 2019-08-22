![](https://img.shields.io/pypi/v/foliantcontrib.meta.svg)

# Metadata for Foliant

This extension adds the `meta generate` command to Foliant, which generates the yaml-file with project metadata. It also allows to add other meta commands `meta <command>` which use the generated metadata.

It also adds the preprocessor `meta` which removes metadata blocks from the documents before builds and allows inserting formatted strings on the place of meta blocks, based on specific metadata keys.

## Installation

```bash
$ pip install foliantcontrib.meta
```

## Specifying metadata

Metadata may be specified in the beginning of a Markdown-file using [YAML Front Matter](http://www.yaml.org/spec/1.2/spec.html#id2760395) format:

```yaml
---
id: MAIN_DOC
title: Description of the product
key: value
---
```

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

## `meta` preprocessor

`meta` preprocessor allows you to remove metadata from your Markdown source files before build. It may be necessary if some backend doesn't accept the YAML Front Matter syntax.

This preprocessor also offers you a feature which we call *seeds*:

Seeds are little string templates which will may be used to add some text after the metadata block in the resulting document, if specific keys were mentioned in the metadata. Details in the **Seeds** section.

### Usage

Add `meta` preprocessor to your `preprocessors` section of foliant.yml and specify all your seeds:

```yaml
preprocessors:
    - meta:
        delete_meta: true
        seeds:
            section: '*Section "{value}"*'
            id: <anchor>{value}</anchor>
```

`delete_meta`
:   If set to `true` — metadata block will be deleted from the document before build. Default: `false`

`seeds`
:   Seeds dictionary. Details in the next section.

### Seeds

Seeds allow you to add small chunks of text based on specific keys mentioned in the metadata block. For example, if you wish to add a small subcaption at the beginning of the document, which will use this document's title, add the `title` seed:

```yaml
preprocessors:
    - meta:
        seeds:
            title: '*Section "{value}"*'
```

If we have a meta block like this in our document:

```yaml
---
ID: legal_info
relates: index.md
title: Legal information
---

# Terms of use
```

Preprocessor will notice that `title` key was used in the meta block, and will add the seed with `{value}` placeholder replaced by the value of the `title` field:

```
*Section "Legal information"

# Terms of use
```
