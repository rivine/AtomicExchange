#!/bin/bash

# Start the first process

zerotier cli join c7c8172af1387fb0
bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

/bin/bash

