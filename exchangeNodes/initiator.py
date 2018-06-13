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

    def __init__(self, init_amount, part_amount, host,dry_run):
        
        self.init_amount = init_amount
        self.part_amount = part_amount
        self.dry_run = dry_run
        self.host = host

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
        #####################

        # Step 1 - Initiating Exchange, Confirming amounts, exchanging recipient addresses for Contracts

            # Opening Connection
        channel = grpc.insecure_channel(self.host + ':50051')
        stub = atomicswap_pb2_grpc.AtomicSwapStub(channel)

            # Generate Initiator Address on Participant chain
        self.init_addr = self.execute("tfchainc wallet address")[21:] # removing substring, JSON output in future?

            # RPC #1 to Participant,
            # IF Participant agrees with amounts,
            # Returns Participant Address 
        response = stub.ProcessInitiate(atomicswap_pb2.Initiate(init_amount=self.init_amount, part_amount=self.part_amount, init_addr=self.init_addr))

            # Print Step Info
        print_json(1, "Received confirmation from Participant, Exchanged recipient addresses", self.step_one_data(response))


        # Step 2 - Initiator Atomicswap Contract with Participant address

            # Create Atomicswap contract on Initiator chain using Participant address as Redeem Recipient
        init_ctc_json = self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 initiate {} {}".format(response.part_addr, self.init_amount))

            # Convert JSON output to Python Object
        init_ctc = json2obj(init_ctc_json)

            # RPC #2 to Participant, 
            # IF Participant agrees with the Initiator Contract,
            # Returns Participant Contract Redeem Address
        response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap(init_ctc_redeem_addr=init_ctc.redeemAddr, init_ctc_hex=init_ctc.contractHex, init_ctc_tx_hex=init_ctc.transactionHex, hashed_secret=init_ctc.hashedSecret))

            # Print Step Info
        print_json(2, "Atomicswap Contracts created, waiting until visible", self.step_two_data(init_ctc, response))

            # Waiting for TF Participant contract to be visible
        seconds_waited = 0
        print("Waiting for 600 seconds")
        while seconds_waited <= 600: # 600s = 10m, based off of Block Creation Time graph here: https://explorer.testnet.threefoldtoken.com/graphs.html
            sys.stdout.write("\r" + "Waited for: " + str(seconds_waited) + "s")
            sys.stdout.flush()
            time.sleep(1)
            seconds_waited += 1


        # Step 3 - Initiator Fulfills Participant Contract with Redeem Transaction, Reveals Secret

            # Make Redeem Transaction

        self.execute("tfchainc atomicswap redeem {} {}".format(response.part_ctc_redeem_addr, init_ctc.secret))
            
            # RPC #3 to Participant,
            # IF Participant makes Redeem Transaction,
            # Returns a Finished = True message
        response = stub.ProcessRedeemed(atomicswap_pb2.InitiatorRedeemFinished(secret=init_ctc.secret))

            # Print Step Info
        print_json(3, "Redeem Transactions created, Atomicswap Finished", self.step_three_data(response))


    #########################
    # r = response
    # ic = init_ctc
    #########################

    def step_one_data(self, r):
        data = {}
        data['participantAmount'] = self.part_amount
        data['initiatorAmount'] = self.init_amount
        data['participantAddress'] = r.part_addr
        data['initiatorAddress'] = self.init_addr
        return data

    def step_two_data(self, ic, r):
        data = {}
        data['initiatorContractRedeemAddress'] = ic.redeemAddr
        data['initiatorContractContractHex'] = ic.contractHex
        data['initiatorContractTransactionHex'] = ic.transactionHex
        data['participantContractRedeemAddress'] = r.part_ctc_redeem_addr
        data['initiatorAddress'] = self.init_addr
        return data

    def step_three_data(self, r):
        data = {}
        data['atomicswapFinished'] = r.finished
        return data


if __name__ == '__main__':
    
    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="init_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="part_amount", default=True,
                    help="The amount of the other partners currency to swap")

    parser.add_option("-i", "--ipaddr",
                    dest="host", default=True,
                    help="The host")

    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

    (options, args) = parser.parse_args()
    dry_run = options.dry_run
  
    atomic_swap = AtomicSwap(float(options.init_amount), float(options.part_amount), options.host, dry_run)
    atomic_swap.run()
