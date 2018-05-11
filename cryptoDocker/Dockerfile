FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y build-essential libtool autotools-dev autoconf libssl-dev libboost-all-dev software-properties-common python-software-properties git
RUN add-apt-repository ppa:bitcoin/bitcoin
RUN add-apt-repository ppa:longsleep/golang-backports

RUN apt-get update

RUN apt-get install -y  golang-go 

#golang
RUN apt-get install -y bitcoind
RUN mkdir /root/.bitcoin/
RUN mkdir -p /usr/local/go

#ENV GOROOT=/usr/local/go
#ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin/

RUN go get -u github.com/threefoldfoundation/tfchain/cmd/...

COPY bitcoin.conf /root/.bitcoin/
COPY btcatomicswap /bin/
#CMD ["bitcoind"]
CMD bitcoind -daemon && tfchaind --network testnet

#