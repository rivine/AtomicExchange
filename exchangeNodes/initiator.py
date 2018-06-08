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

    def __init__(self, init_amount, part_amount, dry_run):
        
        self.init_amount = init_amount
        self.part_amount = part_amount
        self.dry_run = dry_run

    def execute(self, process):
 
        if self.dry_run:
            dry = InitiatorDryRun(self.init_amount, self.part_amount)
            return dry.processCommand(process)
        
        process = os.popen(process)
        output = reprocessed = process.read()
        process.close()
        
        return output.rstrip()
        
    def run(self):

        #######GLOSSARY######
        # init = initiator
        # part = participant
        # ctc = contract
        # tx = transaction
        # addr = address
        # o = output
        # r = response
        #####################

        # Step 1 - Initiating Exchange

            # Opening Connection
        channel = grpc.insecure_channel('localhost:50051')
        stub = atomicswap_pb2_grpc.AtomicSwapStub(channel)

            # RPC #1 to Participant,
            # IF Participant agrees with amounts,
            # Returns Participant Address 
        response = stub.ProcessInitiate(atomicswap_pb2.Initiate(init_amount=self.init_amount, part_amount=self.part_amount))

            # Generate Initiator Address on Participant chain
        self.init_addr = self.execute("tfchainc wallet address")[21:] # removing substring, JSON output in future?

            # Print Step Info
        print_json(1, "Get Confirmation From Participant", self.step_one_data(response))


        # Step 2 - Initiator Atomicswap Contract with Participant address
            
            # Create Atomicswap contract on Initiator chain using Participant address
        init_ctc_json = self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 initiate {} {}".format(response.part_addr, self.init_amount))

            # Convert JSON output to Python Object
        init_ctc = json2obj(init_ctc_json)       

            # RPC #2 to Participant, 
            # IF Participant agrees with the Initiator Contract,
            # Returns Participant Contract Redeem Address
        response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap(init_ctc_redeem_addr=init_ctc.hash, contract=init_ctc.contract, transaction=init_ctc.contractTransaction, init_addr=self.init_addr))
            
            # Print Step Info
        print_json(2, "Create Initiator Contract", self.step_two_data(init_ctc))

            # Waiting for TF Participant contract to be visible
        time.sleep(180)


        # Step 3 - Initiator Audits Participant Contract & Fulfills it with Redeem Transaction, Reveals Secret

        ####################SKIPPING AUDIT STEP FOR POC###################

            # Wait for Enough Confirmations before Auditing Participant Contract
        # self.waitForConfirmsTF(response.part_ctc_redeem_addr)

            # Audit Participant Contract
        # tft_atomicswap_json = self.execute("tfchainc atomicswap --encoding json auditcontract {} --amount {} --min-duration {} --receiver {} --secrethash {}".format(response.part_redeem_addr, self.part_amount, "20h", self.init_addr, init_ctc.hash ))
        # tft_atomicswap = json2obj(tft_atomicswap_json)

        # print_json(3, "Audit Participant Contract", self.step_three_json(init_ctc, tft_atomicswap))
        
        # Uncomment when we have JSON output properly working
        #if(tft_atomicswap.verifications.matchAll == False):
        #    exit(1) #redeem my money after 24h

        ####################SKIPPING AUDIT STEP FOR POC###################

            # Make Redeem Transaction
        init_redeem_tx_json = self.execute("tfchainc atomicswap redeem {} {}".format(response.part_redeem_addr, init_ctc.secret))
        init_redeem_tx = json2obj(init_redeem_tx_json)

        # check if redeem success here
        # self.waitForConfirmsTF(init_redeem_tx.tx_addr)
        # FUNCTION NEEDS TESTING FIRST, relies on JSON output
            
            # RPC #3 to Participant, 
            # IF Participant makes Redeem Transaction,
            # Returns a Finished = True message
        response = stub.ProcessRedeemed(atomicswap_pb2.RedeemFinished(finished=True, tx_addr=init_redeem_tx.tx_addr))

            # Print Step Info
        print_json(4, "Initiator makes Redeem Transaction, Reveals Secret", self.step_four_data(response, init_ctc))   
        

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

    def step_one_data(self, r):
        data = {}
        data['participantAmount'] = self.part_amount
        data['initiatorAmount'] = self.init_amount
        data['participantAddress'] = r.part_addr
        data['initiatorAddress'] = self.init_addr
        return data

    def step_two_data(self, ic):
        data = {}
        data['hash'] = ic.hash
        data['contract'] = ic.contract
        data['contractTransaction'] = ic.contractTransaction
        data['initiatorAddress'] = self.init_addr
        return data

    def step_three_data(self, ic, pc):
        data = {}

        contractValue = {}
        contractValue['expected'] = self.part_amount
        contractValue['actual'] = pc.contractValue
        contractValue['match'] = pc.contractValueMatch
        data['contractValue'] = contractValue

        recipientAddress = {}
        recipientAddress['expected'] = self.init_addr
        recipientAddress['actual'] = pc.recipientAddress
        recipientAddress['match'] = pc.recipientAddressMatch
        data['address'] = recipientAddress

        lockTime = {}
        lockTime['expected'] = ">20"
        lockTime['actual'] = pc.lockTime
        data['lockTime'] = lockTime
        
        secretHash = {}
        secretHash['expected'] = ic.hash
        secretHash['actual'] = pc.hash
        secretHash['match'] = pc.hashedSecretMatch
        data['hash'] = secretHash        

        return data

    def step_four_data(self, r, ic):
        data = {}
        data['participantRedeemAddress'] = r.part_redeem_addr
        data['secret'] = ic.secret
        return data

    def step_five_data(self):
        data = {}
        data['finished'] = 'true'
        return data



if __name__ == '__main__':
    
    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="init_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="part_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

   
    
    (options, args) = parser.parse_args()
    dry_run = options.dry_run
  
    atomic_swap = AtomicSwap(float(options.init_amount), float(options.part_amount), dry_run)
    atomic_swap.run()
