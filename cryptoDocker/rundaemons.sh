#!/bin/bash

# Start the first process
bitcoind -daemon

# Start the second process
tfchaind --network testnet &

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

/bin/bash

