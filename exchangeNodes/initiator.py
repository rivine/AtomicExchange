# Initiator class will initiate contact with acceptor to start the atomic swap

from __future__ import print_function

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc
from optparse import OptionParser

import sys
import os
import json
from collections import namedtuple

from dry_run import InitiatorDryRun

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def print_rt(output):
    output = "{}\n".format(str(output))
    sys.stdout.write(output)
    sys.stdout.flush()

def print_json(step, stepName, data):
    jsonObject = {}
    jsonObject['step'] = step
    jsonObject['stepName'] = stepName
    jsonObject['data'] = data
    json_data = json.dumps(jsonObject) 
    json_data = "{}\n".format(str(json_data))  
    sys.stdout.write(json_data)
    sys.stdout.flush()

class AtomicSwap():

    def __init__(self, initiator_amount, acceptor_amount, dry_run):
        
        self.initiator_amount = initiator_amount
        self.acceptor_amount = acceptor_amount
        self.dry_run = dry_run

    def execute(self, process):
 
        if self.dry_run:
            dry = InitiatorDryRun(self.initiator_amount, self.acceptor_amount)
            return dry.processCommand(process)
        
        process = os.popen(process)
        output = reprocessed = process.read()
        process.close()
        
        return output.rstrip()

    def run(self):

        channel = grpc.insecure_channel('localhost:50051')
        stub = atomicswap_pb2_grpc.AtomicSwapStub(channel)

        data = {}
        data['acceptorAmount'] = self.acceptor_amount
        data['initiatorAmount'] = self.initiator_amount
        print_json(1, "initiateExchange", data)

        response = stub.ProcessInitiate(atomicswap_pb2.Initiate(initiator_amount=self.initiator_amount, acceptor_amount=self.acceptor_amount))
        #response.python -m pip install grpcio
        data = {}
        data['address'] = response.acceptor_address
        print_json(2, "receiveAddress", data)

        btc_atomicswap_json = self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate {} {}".format(response.acceptor_address, self.initiator_amount))
        #do atomic swap
        btc_atomicswap = json2obj(btc_atomicswap_json)   

        data = {}
        data['hash'] = btc_atomicswap.hash
        data['contract'] = btc_atomicswap.contract
        data['contractTransaction'] = btc_atomicswap.contractTransaction

        print_json(3, "generateSmartContractInitiator", data)       
  

        initiator_wallet_address =  self.execute("rivinec wallet address")
        data = {}
        data['address'] = initiator_wallet_address
        print_json(4, "generateInitiatorWalletAddress", data)

        response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap(hash=btc_atomicswap.hash, contract=btc_atomicswap.contract, transaction=btc_atomicswap.contractTransaction, initiator_wallet_address=initiator_wallet_address))

        acceptor_swap_address = response.acceptor_swap_address
        #print_rt("Initiator acceptor_swap_address {}".format(acceptor_swap_address))


        audit_swap_json = self.execute("rivinec atomicswap --testnet audit".format(acceptor_swap_address))
        data = {}
        data['hash'] = btc_atomicswap.hash
        data['contract'] = btc_atomicswap.contract
        data['contractTransaction'] = btc_atomicswap.contractTransaction
        data['initiatorWalletAddress'] = initiator_wallet_address
        print_json(5, "sendSmartContractInitiator", data)

        audit_swap = json2obj(audit_swap_json)

        data = {}
        contractValue = {}
        address = {}
        lockTime = {}
        hash = {}
        contractValue['expected'] = self.acceptor_amount
        contractValue['actual'] = audit_swap.contractValue
        data['contractValue'] = contractValue

        lockTime['expected'] = ">20"
        lockTime['actual'] = audit_swap.lockTime
        data['lockTime'] = lockTime

        hash['expected'] = btc_atomicswap.hash
        hash['actual'] = audit_swap.hash
        data['hash'] = hash

        address['expected'] = initiator_wallet_address
        address['actual'] = audit_swap.recipientAddress
        data['address'] = address

        if(float(audit_swap.contractValue) != self.acceptor_amount or int(audit_swap.lockTime) < 20 or audit_swap.hash != btc_atomicswap.hash or audit_swap.recipientAddress != initiator_wallet_address):
            data['contractValid'] = 'false'
            exit(1) #redeem my money after 24h
        else: 
            data['contractValid'] = 'true'

        print_json(6, "auditSmartContractAcceptor", data)    

        redeem_cmd = "rivinec atomicswap redeem {} {} {} {} {} {} {}".format(acceptor_swap_address, self.acceptor_amount, audit_swap.refundAddress, initiator_wallet_address, btc_atomicswap.hash, audit_swap.lockTime, btc_atomicswap.secret)
        
        data = {}
        data['acceptorSwapAddress'] = acceptor_swap_address
        data['acceptorAmount'] = self.acceptor_amount
        data['refundAddress'] = audit_swap.refundAddress
        data['initiatorWalletAddress'] = initiator_wallet_address
        data['hash'] = btc_atomicswap.hash
        data['lockTime'] = audit_swap.lockTime
        data['secret'] = btc_atomicswap.secret

        print_json(7, "redeemFundsInitiator", data)   

        redeem =  self.execute(redeem_cmd)
        #check if redeem success here
        response = stub.ProcessRedeemed(atomicswap_pb2.RedeemFinished(finished=True))
        
        data = {}
        data['finished'] = 'true'
        print_json(8, "redeemFundsInitiatorFinished", data)   



if __name__ == '__main__':
    
    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="initiator_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="acceptor_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

   
    
    (options, args) = parser.parse_args()
    dry_run = options.dry_run
  
    atomic_swap = AtomicSwap(float(options.initiator_amount), float(options.acceptor_amount), dry_run)
    atomic_swap.run()
