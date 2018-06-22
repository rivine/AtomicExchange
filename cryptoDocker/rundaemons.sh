#!/bin/bash

# Start the first process

mkdir -p /crypto/btc
bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb  -d /crypto/tft &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
sleep 5
zerotier-cli join c7c8172af1387fb0
#@todo keep polling until result in atomicExchange bin


#@todo this must be a random password  - add to ui

if [ "$(ls -A /crypto/tft)" ]; then
     echo "Wallet already initialized"
else
    printf 'thisismypw\nthisismypw\n' | tfchainc wallet init > /crypto/tft/seed.out
fi


#cp seed.out /mnt/walletbackup/$(date +%F_%R_%S)_tfchain.seed
#@todo save seed somewhere!!!
printf 'thisismypw\n' | tfchainc wallet unlock

export ATOMIC_JSON=true
apt install -y iputils-ping python-concurrent.futures python-pip
python -m pip install grpcio
python -m pip install grpcio-tools

export QT_WEBGL_WEBSOCKETSERVER_EXTERNAL=$EXTERNALURL$(hostname)
echo $QT_WEBGL_WEBSOCKETSERVER_EXTERNAL
/dist/atomicExchange -platform webgl &

tail -f /dev/null

