#!/bin/bash

port_num="1"
CONTAINER_NAME="ksm_research_report_pdf"
IMAGE_NAME="research_report_pdf"
TAG="0.1"

fastapi_path=$(pwd)


docker run \
    -it \
    -p ${port_num}7000:7000 \
    --name ${CONTAINER_NAME} \
    --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${fastapi_path}:/research_report_pdf \
    -e DISPLAY=$DISPLAY \
    --shm-size 20g \
    --restart=always \
    -w /research_report_pdf \
    ${IMAGE_NAME}:${TAG}
