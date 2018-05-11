# AtomicExchange
POC for Atomic cryptocurreny exchange based on atomic swaps

## Scope
For the first POC the scope is swapping bitcoins (initiator) for TfChain/Rivine (acceptor) tokens.
## Scripts
Two scripts are created. The initator and acceptor scripts. They are essentially a TCP client and server using gRpc to communicate. Both of the parties will use Zerotier for easy, NAT friendly communication.

## Flow
The flow is based on this [readme](https://github.com/rivine/rivine/blob/master/doc/atomicswap/atomicswap.md) and the same binaries are used from within the Python script. The binaries are adjusted so the output is JSON instead of plain text.

Flow overview:

![exchangeflow](exchangeflow.png)

## Docker
In a first phase a Dockerfile was created using to install both the bitcoind and tfchain binaries/daemons. The Docker has both scripts at disposal and can be used to easily initiate a swap.

## Todo
* ~~Create pseudo code for flow~~
* ~~Create Dockerfile with bitcoin binaries~~
* ~~Adjust Dockerfile for tfChain binaries~~
* ~~Create Python script using gRpc based on pseudo code~~
* ~~Prepare environments for first swap (get tokens)~~
* ~~Adjust btcatomic swap binaries for json output~~
* Adjust rivine/tfchain binaries for json output
* Do manual swap
* Add timers/checks in script where it is required
* Do automatic swap
* Finetuning of script
* Add Zerotier to docker so swap is possible in different networks

## Links
[atomic swap documentation](https://github.com/rivine/rivine/blob/master/doc/atomicswap/atomicswap.md)
[Rivine repositories](https://github.com/rivine/rivine)
