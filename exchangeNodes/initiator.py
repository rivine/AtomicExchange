# Initiator class will initiate contact with participant to start the atomic swap

from __future__ import print_function

import grpc
import time

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

    def __init__(self, initiator_amount, participant_amount, dry_run):
        
        self.initiator_amount = initiator_amount
        self.participant_amount = participant_amount
        self.dry_run = dry_run

    def execute(self, process):
 
        if self.dry_run:
            dry = InitiatorDryRun(self.initiator_amount, self.participant_amount)
            return dry.processCommand(process)
        
        process = os.popen(process)
        output = reprocessed = process.read()
        process.close()
        
        return output.rstrip()
        
    def run(self):

        channel = grpc.insecure_channel('localhost:50051')
        stub = atomicswap_pb2_grpc.AtomicSwapStub(channel)

        # Sends call to Participant, confirming amounts and saves response data
        print_json(1, "initiateExchange", self.step_one_json())
        response = stub.ProcessInitiate(atomicswap_pb2.Initiate(initiator_amount=self.initiator_amount, participant_amount=self.participant_amount))
        print_json(2, "receiveAddress", self.step_two_json(response))

        # Uses Participant address from response to create BTC contract
        btc_atomicswap_json = self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate {} {}".format(response.participant_address, self.initiator_amount))
        btc_atomicswap = json2obj(btc_atomicswap_json)   
        print_json(3, "generateSmartContractInitiator", self.step_three_json(btc_atomicswap))  

        # Creates Initiator Address for Participant to create contract with
        initiator_address = self.execute("tfchainc wallet address")
        print_json(4, "generateInitiatorWalletAddress", self.step_four_json(initiator_address))

        # Sends call to other Party, with the scripthash, the contract and transaction hexstrings, and the Initiator TFT address and saves response data
        response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap(hash=btc_atomicswap.hash, contract=btc_atomicswap.contract, transaction=btc_atomicswap.contractTransaction, initiator_address=initiator_address))
        print_json(5, "sendSmartContractInitiator", self.step_five_json(btc_atomicswap, initiator_address))

        participant_redeem_address = response.participant_redeem_address
        #print_rt("Initiator participant_redeem_address {}".format(participant_redeem_address))

        # Wait for Enough Confirmations before Auditing Participant Contract
        self.waitForConfirmsTF(participant_redeem_address)

        # Audit Participant Contract
        audit_swap_json = self.execute("tfchainc atomicswap audit {}".format(participant_redeem_address))
        audit_swap = json2obj(audit_swap_json)

        data = {}
        contractValue = {}
        address = {}
        lockTime = {}
        hash = {}
        contractValue['expected'] = self.participant_amount
        contractValue['actual'] = audit_swap.contractValue
        data['contractValue'] = contractValue

        lockTime['expected'] = ">20"
        lockTime['actual'] = audit_swap.lockTime
        data['lockTime'] = lockTime

        hash['expected'] = btc_atomicswap.hash
        hash['actual'] = audit_swap.hash
        data['hash'] = hash

        address['expected'] = initiator_address
        address['actual'] = audit_swap.recipientAddress
        data['address'] = address

        # Checking if expected values and actual ones match
        if(float(audit_swap.contractValue) != self.participant_amount or int(audit_swap.lockTime) < 20 or audit_swap.hash != btc_atomicswap.hash or audit_swap.recipientAddress != initiator_address):
            data['contractValid'] = 'false'
            exit(1) #redeem my money after 24h
        else: 
            data['contractValid'] = 'true'

        print_json(6, "auditSmartContractparticipant", data)    

        redeem_cmd = "tfchainc atomicswap redeem {} {}".format(participant_redeem_address, btc_atomicswap.secret)
        
        data = {}
        data['participantSwapAddress'] = participant_redeem_address
        data['secret'] = btc_atomicswap.secret
        print_json(7, "redeemFundsInitiator", data)   

        redeem_json = self.execute(redeem_cmd)
        redeem = json2obj(redeem_json)

    
        #check if redeem success here
        self.waitForConfirmsTF(redeem.transaction_address)

        response = stub.ProcessRedeemed(atomicswap_pb2.RedeemFinished(finished=True, txID=redeem.transaction_address))
        
        data = {}
        data['finished'] = 'true'
        print_json(8, "redeemFundsInitiatorFinished", data)

    def waitForConfirmsTF(self, hash):
        # Get Info from Explorer related to Address
        txInfo_json = self.execute("tfchainc explore hash "+ hash)
        txInfo = json2obj(txInfo_json)

        # Keep Checking Explorer until we find the Transaction in a Block
        # Should probably have a max number of tries
        while txInfo.transactions.height is None:
            time.sleep(10)
            txInfo_json = self.execute("tfchainc explore hash "+ hash)
            txInfo = json2obj(txInfo_json)

        # Then get current Block Height
        currentBlockHeight = self.execute("tfchainc consensus | grep Height | cut -d' ' -f2")
        
        # Keep Comparing Heights until we have enough difference (confirmations)
        while currentBlockHeight - txInfo.transactions.height < 6:
            time.sleep(10)
            currentBlockHeight = self.execute("tfchainc consensus | grep Height | cut -d' ' -f2")

    def step_one_json(self):
        data = {}
        data['participantAmount'] = self.participant_amount
        data['initiatorAmount'] = self.initiator_amount
        return data

    def step_two_json(self, obj):
        data = {}
        data['address'] = obj.participant_address
        return data

    def step_three_json(self, obj):
        data = {}
        data['hash'] = obj.hash
        data['contract'] = obj.contract
        data['contractTransaction'] = obj.contractTransaction
        return data

    def step_four_json(self, addr):
        data = {}
        data['address'] = addr
        return data

    def step_five_json(self, obj, addr):
        data = {}
        data['hash'] = obj.hash
        data['contract'] = obj.contract
        data['contractTransaction'] = obj.contractTransaction
        data['initiatorWalletAddress'] = addr
        return data

    def step_six_json(self, obj):
        data = {}

        return data

    def step_seven_json(self, obj):
        data = {}

        return data

    def step_eight_json(self, obj):
        data = {}

        return data



if __name__ == '__main__':
    
    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="initiator_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="participant_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

   
    
    (options, args) = parser.parse_args()
    dry_run = options.dry_run
  
    atomic_swap = AtomicSwap(float(options.initiator_amount), float(options.participant_amount), dry_run)
    atomic_swap.run()
