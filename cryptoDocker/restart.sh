#!/bin/bash
kill -9 $(pgrep atomicExchange)
nohup /dist/atomicExchange -platform webgl &
exit