![coverage 67%](https://img.shields.io/badge/coverage-55%25-orange)  ![open issues](https://img.shields.io/github/issues/kevindurston21/YANOM-Note-O-Matic)  ![License](https://img.shields.io/github/license/kevindurston21/YANOM-Note-O-Matic)  ![version tag](https://img.shields.io/github/v/tag/kevindurston21/YANOM-Note-O-Matic)

# YANOM - Yet Another Note-O-Matic
YANOM - stands for Yet Another Note-O-Matic. 

YANOM is a file converter to support the use of non-proprietary open file formats for note-taking systems.

It achieves this by converting proprietary note system formats into Markdown or HTML files.  

Additionally, YANOM has the capability to add support for modified Markdown formats used by specific Markdown note-taking system, for example Obsidian image tags are formatted to support image sizing.

## YANOM's Goals
- To be a user-friendly tool anybody can use, with documentation that is detailed enough for any user to install and use.
- Incrementally support additional proprietary formats and open file formats when possible.

# Sections in this read me are
- [YANOM - Yet Another Note-O-Matic](#yanom---yet-another-note-o-matic)
  * [YANOM's Goals](#yanom-s-goals)
- [Sections in this read me are](#sections-in-this-read-me-are)
  * [YANOM Note-O-Matic wiki](#yanom-note-o-matic-wiki)
  * [Version 1.1.0 capabilities](#version-110-capabilities)
    + [Current functionality](#current-functionality)
  * [Getting Started](#getting-started)
    + [Prerequisites](#prerequisites)
      - [Prerequisites source code](#prerequisites-source-code)
      - [Prerequisite for the Debian packaged version](#prerequisite-for-the-debian-packaged-version)
      - [No prerequisites Windows and Mac OSX packaged versions](#no-prerequisites-windows-and-mac-osx-packaged-versions)
    + [Using the pre-built packaged versions for Debian linux, windows and Mac OSX](#using-the-pre-built-packaged-versions-for-debian-linux--windows-and-mac-osx)
    + [Using the docker image](#using-the-docker-image)
    + [Installing from source code](#installing-from-source-code)
  * [Running the tests](#running-the-tests)
    + [Unit Tests with pytest](#unit-tests-with-pytest)
    + [End-to-end tests](#end-to-end-tests)
  * [Deployment](#deployment)
  * [Contributing](#contributing)
  * [Versioning](#versioning)
  * [Change log](#change-log)
  * [Authors](#authors)
  * [License](#license)
  * [Acknowledgments](#acknowledgments)

## YANOM Note-O-Matic wiki
The [YANOM wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) explains features, functionality, instalation and use in greater detail than this read me.

## Version 1.2.0 capabilities 
- Conversion of Synology Note-Station files to markdown or html.  [Full details of the supported features and examples](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/note-station-conversion-details.md) are in the wiki. 
- Conversion between Markdown formats
- HTML to Markdown and Markdown to HTML

YANOM only exports to HTML or Markdown.

Future versions will support conversion from additional proprietary file formats.  

### Current functionality

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
  - QOwnNotes optimised markdown-strict
- Note content that will be converted successfully
  - Headers
  - Bulleted lists
  - Numbered lists
  - Checklists
  - Tables
  - Images 
  - Image width where supported in Markdown 
  - IFrames 
  - Metadata - support JSON, TOML or YAML front matter, and `meta` tags in HTML.  
    - It is also possible include the metadata as plain text at the top of the exported file
    - Option to discard metadata
  - Tags 
    - included in front matter, html header or as plain text with an optional prefix character
    - option to split grouped tags photography/landscape/winter becomes #photography, #landscape, #winter
    - option to remove spaces from tag names, spaces are replaced with hyphen `-`
  - File attachments are maintained
  - Note-Station specific features
    - Charts are recreated.  Options to place an image, data table of the chart data and, a link to a csv file on the exported page.      
    - Links between note pages.
      - For Note-Station most of the time this will be successful.  However, there are some limitations and the [Synology Note-Station Links to Other Note Pages](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/Synology-Note-Station-Links-to-Other-Note-Pages) wiki page has examples of the possible issues and solutions for them.
    - Note-Station audio notes - are attached as an attachment
    - Option to include creation time in file name

The formatting for QOwnNotes and Obsidian are variations on common Markdown formats optimised for those note systems.

## Getting Started

Packaged versions of YANOM have been created, please check the [WIKI](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) for details on how to install those.

The wiki also includes more detailed instructions on [installing and using the source code](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) than can be easily documented here.


### Prerequisites

#### Prerequisites source code
YANOM relies on a python environment when run form source code.  

1. You will need to have a working installation of Python 3.6 or higher.  Details of how to instal python and the instalation files can be found on the [python website](https://www.python.org/downloads/)
2. Once Python is installed, install pipenv using `pip install pipenv`.
3. If using PyCharm - Edit your yanom.py Run time settings from the menu 'Run' -> 'Edit configuration..' and tick the "Emulate terminal in output console" option in the 'Execution' section.  This is required for the interactive command line to run.

YANOM also requires Pandoc.  [Pandoc](https://pandoc.org/installing.html) v1.16 or higher should be used and ideally 2.11 or higher as that is where most testing has been done.

#### Prerequisite for the Debian packaged version
Pandoc is required to be installed.

#### No prerequisites Windows and Mac OSX packaged versions
The packaged versions include the required python environment and pandoc.


### Using the pre-built packaged versions for Debian linux, windows and Mac OSX

Packaged versions of YANOM are available.  Please see the wiki for how to install and use them.

Also, please note the Mac OSX package is slow to start and can take 15 or more seconds to launch. Running a second time from the same terminal window it is usualy just a few seconds.

### Using the docker image
A docker image has been created and is available on [docker hub](https://hub.docker.com/r/thehistorianandthegeek/yanom).  This has pandoc pre-installed, and the docker image is the simplest way to quickly use YANOM and cleanly remove it and pandoc after use.

For further information on the duse of the YANOM docker image please check the [wiki page](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/Installing YANOM using Docker.md)

### Installing from source code

Download the source code from [git hub](https://github.com/kevindurston21/YANOM-Note-O-Matic) 

Un-zip the downloaded file.

Use `pipenv install` to configure a virtual environment and install the required dependencies.  If you are gogint o develop the code use `pipenv install --dev` to install additional devleopment dependencies.

>NOTE it has been seen in some linux versions that a dependency for the package `toml` was not installed automatically.   The symptoms seen were that when a file was converted using `toml` as the front matter format YANOM would crash.  The workaround was to use `pipenv install toml` and then YANOM would run OK.

At the command line type `python yanom.py`  if you wish to add command line arguments you just add them like this `python yanom.py --source notes`

For details of the command line options and how to use YANOM please refer to the [Using YANOM](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/using-yanom.md) wiki page


## Running the tests

### Unit Tests with pytest
There are some unit tests written for YANOM however they also run with pytest.  Some tests were created to run with unittest, but these also run with pytest.  

Please refer to the [test folder](test) for the test files.

Install [pytest](https://docs.pytest.org/en/6.2.x/getting-started.html) for testing and [pytest-cov](https://pypi.org/project/pytest-cov/) for coverage reports.

You can run all tests and create html coverage report if you use this command in the root of the project

`pytest --cov-report html:cov_html test/ --cov=src`

Current coverage is currently 55%

### End-to-end tests

Only a simple manual end-to-end test process exists.

Conversion is made from the `test.nsx` file to Markdown, using each combination of settings.

One set tof the markdown files generated form the `test.nsx` file is converted to html. 

The generated html files are then converted back into a Markdown format.

## Deployment

Deploying source code to a live environment is addressed in the [wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki)

Deployment of packages is achieved using pyinstaller.  For details see the [wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki)

## Contributing
Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on our code of conduct.

Please read [CONTRIBUTING.md](docs/contributing.md) for the process for submitting pull requests to us.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/kevindurston21/YANOM-Note-O-Matic/tags).

## Change log
Please see [CHANGELOG.md](CHANGELOG.md)

## Authors

* **Kevin Durston**

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

- [Maboroshy](https://github.com/Maboroshy) for showing that dissecting an NSX file was possible
- Django Software Foundation and individual contributors for use of the path cleaning function that was modified for use in YANOM.
