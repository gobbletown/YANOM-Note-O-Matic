#! /bin/bash
# USAGE
# From root of yanom project `bash ./scripts/build-ubuntu-focal-package.sh`
# add `test` as an argument to NOT delete the container and image
# AND to be placed in the container for testing
# Docker image will be created, executable generated and copied out to project dist folder
APP_NAME="yanom"
APP_TAR="yanom1.2.0-ubuntu-focal-20.04.tar.gz"
DEV_IMAGE="yanom-dev-ubuntu-focal"
DEV_DOCKERFILE_PATH="dockerfiles/yanom-ubuntu-focal-20210416-dev/Dockerfile"
PROD_DIST_PATH="dist"

# Build docker image to create single file package
docker ps -aq --filter "name=$DEV_IMAGE" | grep -q . && docker stop $DEV_IMAGE && docker rm -fv $DEV_IMAGE
docker build -t $DEV_IMAGE:latest -f $DEV_DOCKERFILE_PATH .
docker container create --name $DEV_IMAGE $DEV_IMAGE:latest
docker cp $DEV_IMAGE:/app/"$APP_TAR" $PROD_DIST_PATH
if ! [ "$1" == "test" ]
then
  docker rm -f $DEV_IMAGE
  docker image rm -f $DEV_IMAGE:latest
else
  docker ps -aq --filter "name=$DEV_IMAGE" | grep -q . && docker stop $DEV_IMAGE && docker rm -fv $DEV_IMAGE
  docker run -it --name $DEV_IMAGE -v ~/$APP_NAME-data:/app/$APP_NAME/data $DEV_IMAGE:latest
fi