#!/bin/bash

# Start the first process


bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
sleep 5
zerotier-cli join c7c8172af1387fb0

tail -f /dev/null