
from concurrent import futures
import time

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc

import os
from optparse import OptionParser
import json
from collections import namedtuple

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)



_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def execute(process):
    process = os.popen(process)
    output = reprocessed = process.read()
    process.close()
    return output.rstrip()

class AtomicSwap(atomicswap_pb2_grpc.AtomicSwapServicer):

    

    def ProcessInitiate(self, request, context):
        global bitcoinaddress
        print("Acceptor: processInitiated")
        print(request.initiator_amount)
        bitcoinaddress = execute('echo 123456789'.rstrip()) #bitcoin-cli gentnewaddress "" legacy
        print("Acceptor: bitcoin address: ")
        print(bitcoinaddress)
        return atomicswap_pb2.InitiateReply(acceptor_address=bitcoinaddress) #if(initiator_amount == request.initiator_amount and acceptor_amount == request.initiator_amount):

        return False
    
    def ProcessInitiateSwap(self, request, context):
        print("processInitiateSwap")
        print(execute('echo {\\"lockTime\\" : \\"48\\", \\"contractValue\\" : \\"5678\\", \\"recipientAddress\\" : \\"123456789\\"}'))
        btc_audit_json =  execute('echo {\\"lockTime\\" : \\"48\\", \\"contractValue\\" : \\"5678\\", \\"recipientAddress\\" : \\"123456789\\"}')#execute('btcatomicswap --testnet auditcontract {} {}'.format(request.contract, request.transaction))
        btc_audit = json2obj(btc_audit_json)
        print("{} > {}".format(btc_audit.lockTime, 40))
        print("{} = {}".format(btc_audit.contractValue, initiator_amount))
        print("{} = {}".format(btc_audit.recipientAddress, bitcoinaddress))
        if(int(btc_audit.lockTime) < 40 or btc_audit.contractValue != initiator_amount or btc_audit.recipientAddress != bitcoinaddress):
            print("Contract invalid")
            return False

        return atomicswap_pb2.AcceptSwap()

    def ProcessRedeemed(self,request,context):
        print("ProcessRedeemed")
        return atomicswap_pb2.RedeemFinished(finished=True)
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atomicswap_pb2_grpc.add_AtomicSwapServicer_to_server(AtomicSwap(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

initiator_amount = 0
acceptor_amount = 0
bitcoinaddress = ""

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="acceptor_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="initiator_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    (options, args) = parser.parse_args()
    
    initiator_amount = options.initiator_amount
    acceptor_amount = options.acceptor_amount

    serve()
