#!/bin/sh
set -e

VERSION=${CIRCLE_BUILD_NUM-Unknown}
QUARTIC_DOCKER_REPOSITORY=${QUARTIC_DOCKER_REPOSITORY-quartic}

docker build -t orinoco .

function build() {
  docker build -t $QUARTIC_DOCKER_REPOSITORY/$1:$VERSION ./$1
  docker push $QUARTIC_DOCKER_REPOSITORY/31:$VERSION
}

build national-grid
build tracker
build tayo
