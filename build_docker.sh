#!/bin/bash

IMAGE_NAME="research_report_pdf"
TAG="0.1"

docker build --no-cache --progress=plain -t ${IMAGE_NAME}:${TAG} . > build.log
