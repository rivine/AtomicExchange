#install
- install npm
- install python


```sh
apt-get install pip
pip install grpcio
pip install grpcio-tools
make
```

# Run acceptor

values are currently hard coded, use these values. 

```sh
python acceptor.py -m 1234 -o 987 -d
```

# Run initiator

values are currently hard coded, use these values. 

```sh
python initiator.py -m 987 -o 1234 -d
```