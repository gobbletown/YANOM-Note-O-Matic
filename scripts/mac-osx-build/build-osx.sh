#! /bin/bash
# USAGE
# Run this script from the root of YANOM project `bash scripts/mac-osx-build/build-osx.sh`
VERSION="1.3.0"
#
cp scripts/mac-osx-build/yanom.spec src/yanom.spec
pipenv shell
cd src
rm -rf dist
pyinstaller --clean yanom.spec
mkdir dist/yanom/data
cp config.ini dist/yanom/data/config.ini
mkdir dist/yanom/pandoc
cp /usr/local/bin/pandoc dist/yanom/pandoc/pandoc
cd dist
zip -r yanom-v"$VERSION"-osx-10.15.7.zip ./yanom
cp yanom-v"$VERSION"-osx-10.15.7 ../../dist
cd ../..
