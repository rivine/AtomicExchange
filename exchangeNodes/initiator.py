# Initiator class will initiate contact with acceptor to start the atomic swap

from __future__ import print_function

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = atomicswap_pb2_grpc.GreeterStub(channel)
    response = stub.AcceptInitiate(atomicswap_pb2.InitiatorSmartContractCreated(hash='8341309506'))

    print("AcceptorSmartContractReceived: " + response.hash)




if __name__ == '__main__':
    run()
