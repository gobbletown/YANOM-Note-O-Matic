![coverage 29%](https://img.shields.io/badge/coverage-29%25-orange)  ![open issues](https://img.shields.io/github/issues/kevindurston21/YANOM-Note-O-Matic)  ![License](https://img.shields.io/github/license/kevindurston21/YANOM-Note-O-Matic)  ![version tag](https://img.shields.io/github/v/tag/kevindurston21/YANOM-Note-O-Matic)  ![](https://img.shields.io/github/pipenv/locked/python-version/kevindurston21/YANOM-Note-O-Matic)

# YANOM Note-O-Matic wiki
YANOM - stands for Yet Another Note-O-Matic. 

YANOM is a file converter to support the use of non-proprietary open file formats for note-taking systems it achieves this by converting proprietary note system formats into Markdown or HTML files.  Additionally, YANOM has the capability to add support for modified Markdown formats used by specific Markdown note-taking system, for example for Obsidian image tags are formatted to support image sizing.

## Version 1.0 capabilities 
- Conversion of Synology Note-Station files to markdown or html.  [Full details of the supported features and examples](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/note-station-conversion-details.md) are in the wiki. 
- Conversion between Markdown formats
- HTML to Markdown and Markdown to HTML

YANOM only exports to HTML or Markdown.

Future versions will support conversion from additional proprietary file formats.  

YANOM Currently can take these inputs.

- NSX file exported from Synology Note-Station.  The Note-Station conversion supports all the features of note station.  Details can be seen on the [Note-Station conversion details](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/note-station-conversion-details.md) page
- html files
- CommonMark  (used by Joplin)
- GFM - Git Flavoured Markdown  (used by Typora, Git Hub, Haroopad)
- Obsidian formatted markdown
- MultiMarkdown
- Pandoc markdown
- Pandoc markdown-strict
- QOwnNotes optimised markdown


YANOM will take any of the above inputs and output them to one of these output formats

- html files
- CommonMark  (Used by Joplin)
- GFM - Git Flavoured Markdown  (Typora, Git Hub, Haroopad)
- Obsidian formatted markdown
- MultiMarkdown (MultiMarkdown Composer)
- Pandoc markdown
- Pandoc markdown-strict
- QOwnNotes an optimised strict markdown

The formatting for QOwnNotes and Obsidian are variations on common Markdown formats optimised for those note systems.

## Getting Started

Packaged versions of YANOM have been created, please check the [WIKI](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) for details on how to install those.

The wiki also includes more detailed instructions on [installing and using the source code](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki) than can be easily documented here.



### Prerequisites

YANOM relies on a python environment when run form source code.  

1. You will need to have a working installation of Python 3.6 or higher.  Details of how to instal python and the instalation files can be found on the [python website](https://www.python.org/downloads/)
2. Once Python is installed, install pipenv using `pip install pipenv`.

The packaged versions include the required python environment.

Both packaged and source code versions require Pandoc.  [Pandoc](https://pandoc.org/installing.html) v1.16 or higher should be used and ideally 2.11 or higher as that is where most testing has been done. 


### Installing

Download the source code from [git hub](https://github.com/kevindurston21/YANOM-Note-O-Matic) 

Un-zip the downloaded file.

Use `pipenv install` to configure a virtual environment and install the required dependencies.

>NOTE it has been seen in some linux versions that a dependency for the package `toml` was not installed automatically.   The symptoms seen were that when a file was converted using `toml` as the front matter format YANOM would crash.  The workaround was to use `pipenv install toml` and then YANOM would run OK.

At the command line type `python yanom.py`  if you wish to add command line arguments you just add them like this `python yanom.py --source notes`

For details of the command line options and how to use YANOM please refer to the [Using YANOM](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki/using-yanom.md) wiki page


## Running the tests

### Unit Tests
There are some unit tests written for YANOM and they use unittest.  

Please refer to the [test folder](../test) for the test files.

a `.converagec` file is included in the root of the project and is set to ignore the `site-packages` and `test` folders

Run all tests using `coverage run --source=src  -m unittest discover` to include all src files including untested ones.

Generate a coverage report using either `coverage report` or `coverage html`

Current coverage is only 29%

### End-to-end tests

Only a simple manual end-to-end test process exists.

Conversion is made from the `test.nsx` file to Markdown, using each combination of settings.

One set tof the markdown files generated form the `test.nsx` file is converted to html. 

The generated html files are then converted back into a Markdown format.

## Deployment

Deploying soucre code to a live environment is addressed in the [wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki)

Deployment of packages is acheived using pyinstaller.  For details see the [deployment page in the wiki](https://github.com/kevindurston21/YANOM-Note-O-Matic/wiki)

## Contributing
Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)for details on our code of conduct.

Please read [CONTRIBUTING.md](docs/contibuting.md) for the process for submitting pull requests to us.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/kevindurston21/YANOM-Note-O-Matic/tags). 

## Authors

* **Kevin Durston**

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- [Maboroshy](https://github.com/Maboroshy) for showing that dissecting an NSX file was possible
- Django Software Foundation and individual contributors for use of the path cleaning function that was modified for use in YANOM.
