## Contributing

Thanks for your interest in contributing to YANOM.  You can contribute in many ways and do not even have to know anything about writing code as without real users feeding back we cannot improve or simplify how YANOM works.

### Where do I go from here?

If you have a general question about YANOM, you can post it on [Discussions].  If you are not sure something is an issue or a feature request post in [Discussions] and we can talk it over and then move the discussion to a new feature request or issue later.

If you've noticed a bug or have a feature request feel free to [raise an issue][new issue].  

Do not be put off if you are not a techie or a coder, part of YANOM's goal is to produce a system that is useable by everybody, and you can help improve the user experience or help writing guides on how to use YANOM from the user point of view.

If you're a coder it's generally best if you get confirmation of your bug or approval for your feature request before starting to code.

You can get an idea of the road map for YANOM from the [Projects] and [Milestones] and see if your idea or feature lines up with the current direction.  If it does not do not worry perhaps you have seen a better way forwards!  We can discuss it and change plans.

### Fork & create a branch if you code

If an issue you raise or feature you would like is something you think you can address, then [fork YANOM].

YANOM has two main branches and attempts to follow the [git flow](https://nvie.com/posts/a-successful-git-branching-model/) approach.  
- The ```main``` branch is for released versions.  Branch from this for a bug fix to the currently released version.
- The ```develop``` branch is the branch to contribute new features to.

A good branch name would be (where issue #29 is the issue/feature you're working on):

```sh
branch swithc main
git checkout -b hotfix/29-fix-commonmark-support
```

```sh
branch swithc main
git flow hotfix start 29-fix-commonmark-support
```

```sh
branch swithc main
git checkout -b feature/29-add-commonmark-support
```

```sh
branch swithc main
git flow feature start 29-add-commonmark-support
```

### Coding style
Currently written in Python...but At some point it is not impossible there may be some C# when OneNote data has to be rescued in Version 2.

I'm not terribly consistent so feel free to clean my code but in general the aim is to:-
- Pythonic... as in  ```import this``` on a python console.
- PEP8 except for line lengths, a few characters over is better than splitting some lines, for example, a long regx expression is not clearer if split into two.
- Shorter methods, generally doing one thing.
- Code that reads well and does not need comments or doc strings to explain things.  Doc strings are good but the code should be readable enough to work out what is going on
- Long method names and file names are fine but look to see if they are actually doing more than one thing.

Of course, I break all of these guidelines at times, I'm still learning every day.

### Testing...

Ah... yes there aren't any tests yet..  If you like writing tests please feel free to create some :-) 

Currently, the test for functionality is to use the Synology note station export file ```test.nsx``` file in the [test](../test) folder.  This should be used to ensure the program tuns and the output is still correct.

Convert the nsx file and choosing the HTML various markdown and export formats will also effectively test the HTML to markdown conversion (not yet implemented but soon will be....) as this is the actual conversion used after the Synology data has been cleaned for conversion.


### Keeping your Pull Request updated
Please "rebase", if your branch has fallen behind the commits on develop or main, before submitting a pull request so your code is easier to merge.  You may also be asked to rebase again if there have been a lot of code changes since your PR was submitted.

To learn more about rebasing in Git, there are a lot of [good][git rebasing]
[resources][interactive rebase] but here's a suggested workflow:

```sh
git checkout feature/29-add-commonmark-support
git pull --rebase upstream develop
git push --force-with-lease feature/29-add-commonmark-support
```



[new issue]: https://github.com/kevindurston21/YANOM-Note-O-Matic/issues/new/choose
[fork YANOM]: https://help.github.com/articles/fork-a-repo
[make a pull request]: https://help.github.com/articles/creating-a-pull-request
[git rebasing]: http://git-scm.com/book/en/Git-Branching-Rebasing
[interactive rebase]: https://help.github.com/en/github/using-git/about-git-rebase
[Discussions]: https://github.com/kevindurston21/YANOM-Note-O-Matic/discussions
[Projects]: https://github.com/kevindurston21/YANOM-Note-O-Matic/projects
[Milestones]: https://github.com/kevindurston21/YANOM-Note-O-Matic/milestones
[git flow]: https://nvie.com/posts/a-successful-git-branching-model/
