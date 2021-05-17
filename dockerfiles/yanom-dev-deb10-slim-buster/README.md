# About the `yanom-dev-deb10-slim-buster` Docker Image

This Dockerfile will 
 - Build an image based off an official python image
 - Uses the YANOM source code to build a pyinstaller package
 - Moves the package into a folder caled `yanom`, adds a `data` directory to it and a copy of `config.ini`
 - Creates a tarball of the yanom folder


This docker file is used along with the `yanom-prod-deb10-slim-buster` dockerfile to produce a deployable docker image.

There is a script `scripts/build-docker-image.sh` that will automate the process

## Additional files in this folder
`.dockerignore` can be used to minimise the ammount coppied to the image
`yanom.spec` is a yanom.spec file that is used by pyinstaller inside the docker image.  Note- a generic yanom.spec can not be created on the fly as pyinstaller can not find `pyfiglets` without a path in the `data` entry of the spec file.

`datas=[('/usr/local/lib/python3.9/site-packages/pyfiglet', './pyfiglet')],`