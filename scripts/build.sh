#!/bin/sh
set -e

VERSION=${CIRCLE_BUILD_NUM-Unknown}
QUARTIC_DOCKER_REPOSITORY=${QUARTIC_DOCKER_REPOSITORY-quartic}

docker build -t orinoco:$VERSION .
docker build -t $QUARTIC_DOCKER_REPOSITORY/national-grid:$VERSION ./national-grid

docker push $QUARTIC_DOCKER_REPOSITORY/national-grid:$VERSION
