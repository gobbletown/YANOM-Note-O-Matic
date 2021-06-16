#! /bin/bash
# USAGE
# Run this script from the root of YANOM project `bash scripts/build-docker-image.sh test 2`
# The script takes two arguments -
# First argument is either `push` or `test` push pushes built production image to docker hub if already logged in
# if `test` is used then images are NOT pushed to docker hub and a container is run using a data directory with the
# path of `~/yanom-data`.  If the directory `~/yanom-data` does not exist it will be created
# if `push` is used the `dev` image and container are removed
#
# Second argument is a docker build number this is a positive value or if left blank it will use version `0`
# NOTE if using `push` it will add an the number to the end of the version number image - so '2' would add `-2`
# to the version image tag e.g. `1.2.0-2`.  If the second argument is zero or missing push will push latest and
# an image tag image e.g. `1.2.0`
APP_NAME="yanom"
VERSION="1.3.0"
APP_TAR="yanom-$VERSION-debian10-slim-buster.tar.gz"
DOCKER_REPO="thehistorianandthegeek"
DEV_IMAGE="yanom-dev-deb10"
DEV_DOCKERFILE_PATH="dockerfiles/yanom-dev-deb10-slim-buster"
PROD_DOCKERFILE_PATH="dockerfiles/yanom-prod-deb10-slim-buster"
PROD_DIST_PATH="dist"
BUILD_NUMBER=0
if [ "$2" ] && [ "$2" -gt 0 ]
then
  BUILD_NUMBER=$2
fi
# refresh requirements.txt  this adds time to build but helps when forget to update requirements!
echo updating requirements.txt
pipenv lock --requirements > requirements.txt

# copy in required dockerignore file
cp $DEV_DOCKERFILE_PATH/.dockerignore .dockerignore

# Build docker image to create single file package
docker ps -aq --filter "name=$DEV_IMAGE" | grep -q . && docker stop $DEV_IMAGE && docker rm -fv $DEV_IMAGE
docker build --build-arg APP_TAR=$APP_TAR -t $DEV_IMAGE:latest -f $DEV_DOCKERFILE_PATH/Dockerfile .
docker container create --name $DEV_IMAGE $DEV_IMAGE:latest
docker cp $DEV_IMAGE:/app/$APP_TAR $PROD_DIST_PATH
if [ "$1" ] && [ "$1" == "push" ]
then
  docker rm -f $DEV_IMAGE
  docker image rm $DEV_IMAGE:latest
fi

## remove the docker ignore file
rm .dockerignore
## Build and push docker production image
docker build --build-arg APP_TAR=$APP_TAR -t $DOCKER_REPO/$APP_NAME:"$VERSION-$BUILD_NUMBER" -t $DOCKER_REPO/$APP_NAME:latest -f $PROD_DOCKERFILE_PATH/Dockerfile .
if [ "$1" ] && [ "$1" == "push" ]
then
  docker push $DOCKER_REPO/$APP_NAME:latest
  if [ "$BUILD_NUMBER" -gt 0 ]
  then
    docker push $DOCKER_REPO/$APP_NAME:"$VERSION-$BUILD_NUMBER"
  fi
  if [ "$BUILD_NUMBER" == 0 ]
  then
    docker push $DOCKER_REPO/$APP_NAME:"$VERSION"
  fi
fi
if [ "$1" ] && [ "$1" == "test" ]
then
  if [ -d ~/$APP_NAME-data ]
  then
    echo "Data Directory Exists"
  else
    mkdir ~/$APP_NAME-data
  fi
  docker ps -aq --filter "name=$APP_NAME" | grep -q . && docker stop $APP_NAME && docker rm -fv $APP_NAME
  docker run -it --name $APP_NAME -v ~/$APP_NAME-data:/app/$APP_NAME/data $DOCKER_REPO/$APP_NAME:latest
fi
