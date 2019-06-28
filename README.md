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

You can also specify metadata in the middle of the document. In this case it should appear just after a heading of any level:

```yaml
## System protocol description

---
title: System protocol
relates: MAIN_DOC
---

```

Each new metadata block means a new section of the chapter.

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

`meta` preprocessor is necessary if you add metadata into the middle of your documents: it removes the metadata blocks before building the document so it won't get to the result.

This preprocessor also offers you a feature which we call *seeds*:

Seeds are little string templates which will appear after the metadata block in the resulting document, if specific keys were mentioned in the metadata. Details in the **Seeds** section.

### Usage

Add `meta` preprocessor to your `preprocessors` section of foliant.yml and specify all your seeds:

```yaml
preprocessors:
    - meta:
        seeds:
            section: '*Section "{value}"*'
            id: <anchor>{value}</anchor>
```

### Seeds

Seeds allow you to add small chunks of text based on specific keys mentioned in the metadata block. For example, if you wish to add a small subcaption at the beginning of every section, which will use this section's name, add a `section` seed:

```yaml
preprocessors:
    - meta:
        seeds:
            section: '*Section "{value}"*'
```

If we have a meta block like this in our document:

```yaml
# Terms of use
---
ID: legal_info
relates: index.md
section: Legal information
---
```

Preprocessor will notice that `section` key was used in the meta block, and will add the seed with `{value}` placeholder replaced by the value of the `section` field:

```
# Terms of use

*Section "Legal information"
```
