#! /bin/bash
# USAGE
# Run this script from the root of YANOM project `bash build-ubuntu-focal-package.sh`
# Docker image will be created, executable generated and copied out to project dist folder
APP_NAME="yanom1-ubuntu-focal-20.04.tar.gz"
DEV_IMAGE="yanom-dev-ubuntu-focal"
DEV_DOCKERFILE_PATH="dockerfiles/yanom-ubuntu-focal-20210416-dev/Dockerfile"
PROD_DIST_PATH="dist/ubuntu-focal-20-04"

# Build docker image to create single file package
docker ps -aq --filter "name=$DEV_IMAGE" | grep -q . && docker stop $DEV_IMAGE && docker rm -fv $DEV_IMAGE
docker build -t $DEV_IMAGE:latest -f $DEV_DOCKERFILE_PATH .
docker container create --name $DEV_IMAGE $DEV_IMAGE:latest
docker cp $DEV_IMAGE:/app/"$APP_NAME" $PROD_DIST_PATH
docker rm -f $DEV_IMAGE
docker image rm $DEV_IMAGE:latest
