#!/bin/bash

# Start the first process

zerotier cli join 28.255.218.251
bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

/bin/bash

