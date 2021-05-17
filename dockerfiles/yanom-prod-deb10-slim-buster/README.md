# About the `yanom-prod-deb10-slim-buster` Docker Image

This Dockerfile will 
 - Build a 'base' image based off an official Debian 10 base image
 - From the 'base' an intermediate image ius built that copies tar ball from the `yanom-dev-deb10-slim-buster` image
 - From the 'base' a final image is built that copies the uncompressed yanom folder from the 'intermediate'
   
The use of the 3 stage build minimises the size of the final deployed production image

There is a script `scripts/build-docker-image.sh` that will automate the process of using the two docker files