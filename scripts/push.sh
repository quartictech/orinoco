VERSION=${CIRCLE_BUILD_NUM-Unknown}
QUARTIC_DOCKER_REPOSITORY=${QUARTIC_DOCKER_REPOSITORY-quartic}

docker push $QUARTIC_DOCKER_REPOSITORY/orinoco:$VERSION
