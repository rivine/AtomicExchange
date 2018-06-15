#!/bin/bash
kill -9 $(pgrep atomicExchange)
/dist/atomicExchange -platform webgl &