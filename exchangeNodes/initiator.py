# Initiator class will initiate contact with acceptor to start the atomic swap

from __future__ import print_function

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc
from optparse import OptionParser

import os
import json
from collections import namedtuple

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


def execute(process):
    process = os.popen(process)
    output = reprocessed = process.read()
    process.close()
    return output


def run(initiator_amount, acceptor_amount):
    channel = grpc.insecure_channel('localhost:50051')
    stub = atomicswap_pb2_grpc.AtomicSwapStub(channel)


    response = stub.ProcessInitiate(atomicswap_pb2.Initiate(initiator_amount=initiator_amount, acceptor_amount=acceptor_amount))
    #response.python -m pip install grpcio
    print("Initiator: ")
    print(response.acceptor_address)
    #btc_atomicswap_json = Execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate {} {}" % response.acceptor_address, initiator_amount)
    #do atomic swap
    print("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate {} {}".format(response.acceptor_address, initiator_amount))

    btc_atomicswap_json = "{ \"secret\" : \"12345789\", \"hash\" : \"abc12345678098\", \"contractfee\" : \"0.2\", \"refundfee\" : \"0.1\", \"contract\" : \"54345678\", \"contractTransaction\" : \"tx123456\" }"

    print(btc_atomicswap_json)

    btc_atomicswap = json2obj(btc_atomicswap_json)
    
    initiator_wallet_address =  execute("echo 099765432")  #`rivinec wallet address`
    atomicswap_pb2.InitiateSwap(hash=btc_atomicswap.hash, contract=btc_atomicswap.contract, transaction=btc_atomicswap.contractTransaction, initiator_wallet_address=initiator_wallet_address)

    response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap())


    response = stub.ProcessRedeemed(atomicswap_pb2.RedeemFinished())

   



if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="initiator_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="acceptor_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    (options, args) = parser.parse_args()

    run(float(options.initiator_amount), float(options.acceptor_amount))
