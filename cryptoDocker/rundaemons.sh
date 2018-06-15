#!/bin/bash

# Start the first process


bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
sleep 5
zerotier-cli join c7c8172af1387fb0
#@todo keep polling until result in atomicExchange bin


#@todo this must be a random password  - add to ui
printf 'thisismypw\nthisismypw\n' | tfchainc wallet init > /seed.out
cp seed.out /mnt/walletbackup/$(date +%F_%R_%S)_tfchain.seed
#@todo save seed somewhere!!!
printf 'thisismypw\n' | tfchainc wallet unlock


sleep 60
/dist/atomicExchange -platform webgl &

tail -f /dev/null

