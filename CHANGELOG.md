# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows something close to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as there is no public API yet then the following guide applies.

- Increment the patch number when you ship a bug fix
- Increment the minor version number when adding a new feature or set of features and any current bug fixes not yet released
- Increment the major version when significantly overhaul the user interface, or rewrite all internals.

## Unreleased
> These unreleased features are on the develop branch

- Code refactoring

## [1.1.0] - 2021-05-14
### Added
- Support for iframes in HTML to Markdown and NSX files to Markdown
- Progress bars during conversion

### Fixed
- Note-Station program exports the 'My Notebook' with no title.  Now detect this and give the notebook it's 'My Notebook' title.
- Image width detection now detects widths with `px` appended to the width

## [1.0.0] - 2021-05-09
### Initial release functionality

- project [wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) covering installation, use and functionality etc.
- Convert Note-Station `.nsx` export files to Markdown or HTML
- Convert HTML to Markdown
- Convert Markdown to HTML
- Convert Markdown to a different format of Markdown
- List of available Markdown formats that can be used as inputs or outputs
  - CommonMark  (Used by Joplin)
  - GFM - Git Flavoured Markdown  (Typora, Git Hub, Haroopad) 
  - Obsidian formatted markdown 
  - MultiMarkdown (MultiMarkdown Composer) 
  - Pandoc markdown 
  - Pandoc markdown-strict 
  - QOwnNotes optimised markdown-
- Note content that will be converted successfully
  - Headers
  - Bulleted lists
  - Numbered lists
  - Checklists
  - Tables
  - Images 
  - Image width where supported in Markdown 
  - IFrames 
  - Metadata - support JSON, TOML or YAML front matter, and `meta` tags in HTML
  - Tags 
    - included in front matter, html header or as plain text with an optional prefix character
    - option to split grouped tags photography/landscape/winter becomes #photography, #landscape, #winter
    - option to remove spaces from tag names
  - Tags 
  - File attachments are maintained
  - Note-Station specific features
    - Charts are recreated.  An image is placed on the page, along with a data table of the chart data, and a link to a csv file of the data.      
    - Links between note pages.
      - For Note-Station most of the time this will be successful.  However, there are some limitations and the [Synology Note-Station Links to Other Note Pages](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/Synology-Note-Station-Links-to-Other-Note-Pages) wiki page has examples of the possible issues and solutions for them.
    - Note-Station audio notes - are attached as an attachment
    - Option to include creation time in file name

