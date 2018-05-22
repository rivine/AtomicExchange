
from concurrent import futures
import time

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



class AtomicSwap(atomicswap_pb2_grpc.AtomicSwapServicer):
    
    dry_run = False
    initiator_amount = 0
    acceptor_amount = 0
    bitcoinaddress = "" #address generated to receive funds
    contract_address = ""
    initiator_contract = ""
    initiator_transaction = ""

    def __init__(self, initiator_amount, acceptor_amount, dry_run):
        
        self.initiator_amount = initiator_amount
        self.acceptor_amount = acceptor_amount

        self.dry_run = dry_run

    def execute(self, process):

        if self.dry_run:
            dry = AcceptorDryRun(initiator_amount, acceptor_amount)
            return dry.processCommand(process)

        process = os.popen(process)
        output = reprocessed = process.read()
        process.close()
        
        return output.rstrip()

    def ProcessInitiate(self, request, context):
     
        
        print("Acceptor: processInitiated for {} initiator_amount".format(request.initiator_amount))
        self.bitcoinaddress = self.execute("bitcoin-cli gentnewaddress "" legacy") #
        print("Acceptor: got new bitcoin address: {}".format(self.bitcoinaddress))
    
        return atomicswap_pb2.InitiateReply(acceptor_address=self.bitcoinaddress) #if(initiator_amount == request.initiator_amount and acceptor_amount == request.initiator_amount):

        return False
    
    def ProcessInitiateSwap(self, request, context):

    
        print("Acceptor: processInitiateSwap")

        btc_audit_json =  self.execute("btcatomicswap --testnet auditcontract {} {}".format(request.contract, request.transaction)) 
        print(btc_audit_json)
        btc_audit = json2obj(btc_audit_json)
        self.initiator_contract = request.contract
        self.initiator_transaction = request.transaction

        print("Acceptor: Auditing contract: ")
        print("{} > {}".format(btc_audit.lockTime, 40))
        print("{} = {}".format(btc_audit.contractValue, initiator_amount))
        print("{} = {}".format(btc_audit.recipientAddress, self.bitcoinaddress))


        if(int(btc_audit.lockTime) < 40):
            print("Acceptor: contract invalid,locktime > 40 ; {}".format(int(btc_audit.lockTime)))
            return False
        if float(btc_audit.contractValue) != float(initiator_amount):
            print("Acceptor: contract invalid,initiator_amount not equal ")
            return False
        if btc_audit.recipientAddress != self.bitcoinaddress:
            print("Acceptor: Contract invalid, rec address <> bitcoinaddress")
            return False

        rivinec_atomicswap_json = self.execute("rivinec atomicswap --testnet participate {} {} {}".format(request.initiator_wallet_address, acceptor_amount, request.hash))  #"
       
        rivinec_atomicswap = json2obj(rivinec_atomicswap_json)
        self.contract_address = rivinec_atomicswap.contractAddress
        return atomicswap_pb2.AcceptSwap(acceptor_swap_address=rivinec_atomicswap.contractAddress)


    def ProcessRedeemed(self,request,context): 
  
        print("Acceptor: ProcessRedeemed")

        get_secret_cmd = "rivinec --addr explorer.testnet.threefoldtoken.com extractsecret {}".format(self.contract_address)
        explore = json2obj(self.execute(get_secret_cmd))
        
        redeem_cmd = "btcatomicswap --testnet --rpcuser=user --rpcpass=pass redeem {} {} {}".format(self.initiator_contract, self.initiator_transaction, explore.secret)
        redeem = json2obj(self.execute(redeem_cmd))

        
        return atomicswap_pb2.RedeemFinished(finished=True)
        

def serve(initiator_amount, acceptor_amount, dry_run):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atomicswap_pb2_grpc.add_AtomicSwapServicer_to_server(AtomicSwap(initiator_amount, acceptor_amount, dry_run), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)



if __name__ == '__main__':
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

    serve(initiator_amount, acceptor_amount, dry_run)
