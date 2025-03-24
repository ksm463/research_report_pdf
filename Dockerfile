FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

COPY . /research_report_pdf/
WORKDIR /research_report_pdf

RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y software-properties-common && \
    apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils && \
    apt-get install -y python3-pip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN ln -s $(which python3) /usr/bin/python
RUN bash /research_report_pdf/setting-scripts/install_dependencies.sh
RUN pip install --no-cache-dir --no-deps -r /research_report_pdf/setting-scripts/requirements.txt
