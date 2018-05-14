#!/bin/bash

# Start the first process
bitcoind -daemon

# Start the second process
tfchaind --network testnet -M cgtewb &

/bin/bash