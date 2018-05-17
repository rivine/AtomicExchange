FROM ubuntu:16.04

RUN apt-get -qq update
RUN apt-get install -qq -y build-essential libtool autotools-dev autoconf libssl-dev libboost-all-dev software-properties-common python-software-properties git curl
RUN add-apt-repository ppa:bitcoin/bitcoin
RUN add-apt-repository ppa:longsleep/golang-backports

## ZEROTIER
RUN apt-get -y install supervisor && \
    mkdir -p /var/log/supervisor

RUN curl -s https://install.zerotier.com/ |  bash || true
 # rm /var/lib/zerotier-one/zerotier-one.pid || true && \
RUN service zerotier-one stop && \ 
    echo "manual" >> /etc/init/zerotier-one.override
   # rm /var/lib/zerotier-one/identity.secret && \
   # rm /var/lib/zerotier-one/identity.public

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

## /ZEROTIER
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
COPY rundaemons.sh /rundaemons.sh
#CMD ["bitcoind"]
CMD /rundaemons.sh

#

