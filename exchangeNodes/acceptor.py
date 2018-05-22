
from concurrent import futures
import time
import sys

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc

import os
from optparse import OptionParser
import json
from collections import namedtuple

from dry_run import AcceptorDryRun
def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)



_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def execute(process):
    
    global dry_run

    if dry_run:
        dry = AcceptorDryRun()
        return dry.processCommand(process)

    process = os.popen(process)
    output = reprocessed = process.read()
    process.close()
    
    return output.rstrip()
def print_rt(output):
    sys.stdout.write(output)
    sys.stdout.flush()
class AtomicSwap(atomicswap_pb2_grpc.AtomicSwapServicer):

    

    def ProcessInitiate(self, request, context):
        global bitcoinaddress
        
        print_rt("Acceptor: processInitiated for {} initiator_amount".format(request.initiator_amount))
        bitcoinaddress = execute("bitcoin-cli gentnewaddress "" legacy") #
        print_rt("Acceptor: got new bitcoin address: {}".format(bitcoinaddress))
    
        return atomicswap_pb2.InitiateReply(acceptor_address=bitcoinaddress) #if(initiator_amount == request.initiator_amount and acceptor_amount == request.initiator_amount):

        return False
    
    def ProcessInitiateSwap(self, request, context):
        global contractAddress
        global initiator_contract
        global initiator_transaction

        print_rt("Acceptor: processInitiateSwap")

        btc_audit_json =  execute("btcatomicswap --testnet auditcontract {} {}".format(request.contract, request.transaction)) 
        print_rt(btc_audit_json)
        btc_audit = json2obj(btc_audit_json)
        initiator_contract = request.contract
        initiator_transaction = request.transaction

        print_rt("Acceptor: Auditing contract: ")
        print_rt("{} > {}".format(btc_audit.lockTime, 40))
        print_rt("{} = {}".format(btc_audit.contractValue, initiator_amount))
        print_rt("{} = {}".format(btc_audit.recipientAddress, bitcoinaddress))


        if(int(btc_audit.lockTime) < 40 or btc_audit.contractValue != initiator_amount or btc_audit.recipientAddress != bitcoinaddress):
            print_rt("Acceptor: Contract invalid")
            return False

        rivinec_atomicswap_json = execute("rivinec atomicswap --testnet participate {} {} {}".format(request.initiator_wallet_address, acceptor_amount, request.hash))  #"
       
        rivinec_atomicswap = json2obj(rivinec_atomicswap_json)
        contractAddress = rivinec_atomicswap.contractAddress
        return atomicswap_pb2.AcceptSwap(acceptor_swap_address=rivinec_atomicswap.contractAddress)


    def ProcessRedeemed(self,request,context):
        global contractAddress
        global initiator_transaction
        print_rt("Acceptor: ProcessRedeemed")

        get_secret_cmd = "rivinec --addr explorer.testnet.threefoldtoken.com extractsecret {}".format(contractAddress)
        explore = json2obj(execute(get_secret_cmd))
        
        redeem_cmd = "btcatomicswap --testnet --rpcuser=user --rpcpass=pass redeem {} {} {}".format(initiator_contract, initiator_transaction, explore.secret)
        redeem = json2obj(execute(redeem_cmd))

        
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
contractAddress = ""
initiator_contract = ""
initiator_transaction = ""
dry_run = False

if __name__ == '__main__':
    global dry_run
    print_rt("Start")

    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="acceptor_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="initiator_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

    (options, args) = parser.parse_args()
    
    initiator_amount = options.initiator_amount
    acceptor_amount = options.acceptor_amount

    dry_run = options.dry_run
    
    serve()
