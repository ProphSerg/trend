#
# Copyright (c) 2017-2022, The PurpleI2P Project
#
# This file is part of Purple i2pd project and licensed under BSD3
#
# See full license text in LICENSE file at top of project tree
#

ARG I2PD_DIR="/app"

FROM alpine:latest AS builder
LABEL authors="Mikal Villa <mikal@sigterm.no>, Darknet Villain <supervillain@riseup.net>"
LABEL maintainer="R4SAS <r4sas@i2pmail.org>"

LABEL org.opencontainers.image.source=https://github.com/PurpleI2P/i2pd
LABEL org.opencontainers.image.documentation=https://i2pd.readthedocs.io/en/latest/
LABEL org.opencontainers.image.licenses=BSD3

# Expose git branch, tag and URL variables as arguments
ARG GIT_BRANCH="openssl"
ENV GIT_BRANCH=${GIT_BRANCH}
ARG GIT_TAG=""
ENV GIT_TAG=${GIT_TAG}
ARG REPO_URL="https://github.com/PurpleI2P/i2pd.git"
ENV REPO_URL=${REPO_URL}

# 1. Building binary
#   Each RUN is a layer, adding the dependencies and building i2pd in one layer takes around 8-900Mb, so to keep the
#   image under 20mb we need to remove all the build dependencies in the same "RUN" / layer.
#
#   1. install deps, clone and build.
#   2. strip binaries.
#   3. Purge all dependencies and other unrelated packages, including build directory.

RUN apk update \
    && apk --no-cache add make gcc g++ \
        libtool zlib-dev boost-dev build-base openssl-dev openssl miniupnpc-dev git \
        boost-static openssl-libs-static zlib-static \
    && mkdir -p /tmp/build

RUN cd /tmp/build && git clone -b ${GIT_BRANCH} ${REPO_URL} \
    && cd i2pd \
    && if [ -n "${GIT_TAG}" ]; then git checkout tags/${GIT_TAG}; fi \
    && cd contrib && tar zcvf ../certificates.tgz certificates

RUN ln -s /usr/lib /usr/lib/$(c++ -dumpmachine) \
    && cd /tmp/build/i2pd \
    && make -j$(nproc) USE_STATIC=yes USE_UPNP=yes DEBUG=no TORRENTS=no

FROM alpine:latest AS runtime

ARG I2PD_DIR
ARG UID=568
ARG GID=568
ARG TZ=Asia/Omsk
ENV TZ=${TZ}
ENV I2PD="${I2PD_DIR}/i2pd"
ENV DATA_DIR="${I2PD_DIR}/data"

# Установка Временной зоны
RUN apk add --no-cache --update \
    tzdata libstdc++ \
    &&  ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone

COPY --from=builder /tmp/build/i2pd/i2pd ${I2PD_DIR}/
COPY --from=builder /tmp/build/i2pd/certificates.tgz ${I2PD_DIR}/
COPY --from=builder /tmp/build/i2pd/contrib/i2pd.conf ${I2PD_DIR}/i2pd.conf.default
COPY entrypoint.sh ${I2PD_DIR}/
RUN chmod +x ${I2PD_DIR}/entrypoint.sh ${I2PD_DIR}/i2pd

# RUN addgroup -S -g ${GID} qbt \
#     && adduser -S -u ${UID} -G qbt qbt \
#     && chown -R ${UID}:${GID} /app

WORKDIR ${I2PD_DIR}
VOLUME ${DATA_DIR}
#EXPOSE 7070 4444 4447 7656 2827 7654 7650
ENTRYPOINT [ "/app/entrypoint.sh" ]
