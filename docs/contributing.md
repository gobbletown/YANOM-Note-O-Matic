
If you have a general question about YANOM, you can post it on [Discussions].  If you are not sure something is an issue, or a feature request post in [Discussions] and we can talk it over and then move the discussion to a new feature request or issue later.

If you've noticed a bug or have a feature request, [make one][new issue]! Do not be put off if you are not a techie or a coder, part of YANOM's goal is to produce a system that is usable by everybody.

If you're a coder it's generally best if you get confirmation of your bug or approval for your feature request before starting to code.

You can get an idea of the road map for YANOM from the [Projects] and [Milestones] and see if your idea or feature lines up with the current direction.  If your idea does not align to the current direction or priorities perhaps you may have seen a better way forwards!  We can discuss it and perhaps change plans.

- [Fork and create a branch if you code](Contributing.md#fork-and-create-a-branch-if-you-code)
- [Coding style](Contributing.md#coding-style)
- [Testing](Contributing.md#testing)
- [Keeping your Pull Request updated](Contributing.md#keeping-your-pull-request-updated)
- [Information about the project structure and builds](Contributing.md#information-about-the-project-structure-and-builds)

### Fork and create a branch if you code

If an issue you raise or feature you would like is something you think you can address, then [fork YANOM].

YANOM has two main branches and attempts to follow something similar to the [git flow](https://nvie.com/posts/a-successful-git-branching-model/) approach, though use fo gitflow is optional.  

- The ```main``` branch is for released versions.  Branch from this for a bug fix to the currently released version.
- The ```develop``` branch is the branch to contribute new features to or fixes to the current development code.

A good branch name would be, where issue #29 is the issue/feature you're working on, and some examples are:

```sh
branch swithc main
git checkout -b fix-29-fix-commonmark-support
```

```sh
branch swithc main
git flow hotfix start 29-fix-commonmark-support
```

```sh
branch swithc main
git checkout -b feature-29-add-commonmark-support
```

```sh
branch swithc main
git flow feature start 29-add-commonmark-support
```

### Coding style
Currently, written in Python...but At some point it is not impossible there may be some C# when OneNote data has to be rescued in Version 2.

I'm not terribly consistent so feel free to clean my code but in general the aim is to:-
- Pythonic... as in  ```import this``` on a python console.
- PEP8 except for line lengths, a few characters over is better than splitting some lines, for example, a long regx expression is not clearer if split into two.
- Shorter methods, generally doing one thing.
- Code that reads well and does not need comments or doc strings to explain things.  Doc strings are OK, but the code should be readable enough to work out what is going on
- Long method names and file names are fine but look to see if they are actually doing more than one thing.
- having just said do one thing a method that is 'do_something_if_required' is fine if the first part of the method is a test for the need for the method.  ALso setting a path and file name in one method is also OK as closely related, and a "path" can be directory and file name ..so they are "one thing"..

Of course, I break all of these guidelines at times, I'm still learning every day.

### Testing

Ah... yes there are just a few tests written so far.  If you like writing tests please feel free to create some!  A goal will be to improve coverage.

A test for system functionality is to use the Synology note station export file ```test.nsx``` file in the [test](https://github.com/kevindurston21/YANOM-Note-O-Matic/tree/main/test) folder.  This should be used to ensure the program
runs, and the output is still correct.  For example, you can first convert from NSX to markdown, then convert those markdown files to HTML and then convert the HTML back to markdown.


### Keeping your Pull Request updated
Please "rebase", if your branch has fallen behind the commits on develop or main before submitting a pull request.  You may also be asked to rebase again if there have been a lot of code changes since your PR was submitted.

To learn more about rebasing in Git, there are a lot of [good][git rebasing]
[resources][interactive rebase] but here's a suggested workflow:

```sh
git checkout feature/29-add-commonmark-support
git pull --rebase upstream master
git push --force-with-lease feature/29-add-commonmark-support
```

### Information about the project structure and builds

#### `src` folder
- Contains source code
- Sub-directory `data`, this is YANOMs "working directory".  YANOM is hard coded to use a sub-directory called data. Why?  Docker volumes connect to it.
- `data` also contains `config.ini` so it can be edited on a host system using docker, also a folder `logs` is generated for log files in the `data` folder when YANOM runs

#### `scripts` folder
Contains docker build scripts. Why a complex script for the debina10 development and production images?  This could have been done in a single multistage docker file, however the built YANOM executable also needs to be copied out for further distribution so breaking into two builds allows the file to be copied out of the development docker image.

#### `dockerfiles` folder
Each sub-directory will contain a `Dockerfile` and if it builds a YANOM executable there will also include a `yanom.spec` file that is used in the docker image by [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/usage.html).

#### `test` folder
This contains unit test `.py` files and two sub-directories
- `conversion_test_inputs` contains 
  - A Note-Station `test.nsx` export file. This file is used for function testing the entire program.  It cna be used to generate markdown and html files, and those files can then be reconverted to further markdown or html files.
- `conversion_results` contains example outputs generated from the `test.nsx` file.

[new issue]: https://github.com/kevindurston21/YANOM-Note-O-Matic/issues/new/choose
[fork YANOM]: https://help.github.com/articles/fork-a-repo
[make a pull request]: https://help.github.com/articles/creating-a-pull-request
[git rebasing]: http://git-scm.com/book/en/Git-Branching-Rebasing
[interactive rebase]: https://help.github.com/en/github/using-git/about-git-rebase
[Discussions]: https://github.com/kevindurston21/YANOM-Note-O-Matic/discussions
[Projects]: https://github.com/kevindurston21/YANOM-Note-O-Matic/projects
[Miulestones]: https://github.com/kevindurston21/YANOM-Note-O-Matic/milestones
[git flow]: https://nvie.com/posts/a-successful-git-branching-model/