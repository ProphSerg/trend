#!/bin/sh

#set -x

mkdir -p ${DATA_DIR}

if [ "$1" = "--help" ]; then
    set -- ${I2PD} --help
else
    if [ ! -d "${DATA_DIR}/certificates" ]
    then
        cd ${DATA_DIR}
        tar zxvf ../certificates.tgz
        cd /app
    fi

    if [ ! -f "${DATA_DIR}/i2pd.conf" ]
    then
        cp  i2pd.conf.default ${DATA_DIR}/i2pd.conf
    fi
    set -- ${I2PD} --datadir ${DATA_DIR} $@
fi

exec "$@"
