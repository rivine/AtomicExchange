# Initiator class will initiate contact with participant to start the atomic swap

from __future__ import print_function

import grpc
import time

import atomicswap_pb2
import atomicswap_pb2_grpc
from optparse import OptionParser

import sys
import subprocess
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
        
        pro = subprocess.Popen(process, stdout=subprocess.PIPE, 
                            shell=True, preexec_fn=os.setsid) 
        out, err = pro.communicate()
        return out, err, pro.returncode

        
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
        self.init_addr, _, _ = self.execute("tfchainc wallet address")
        self.init_addr = self.init_addr[21:] # removing substring, JSON output in future?
        self.init_addr = self.init_addr.rstrip("\r\n")
            # RPC #1 to Participant,
            # IF Participant agrees with amounts,
            # Returns Participant Address 
      
        response = stub.ProcessInitiate(atomicswap_pb2.Initiate(init_amount=self.init_amount, part_amount=self.part_amount, init_addr=self.init_addr))

            # Print Step Info
        print_json(1, "Received confirmation from Participant, Exchanged recipient addresses", self.step_one_data(response))


        # Step 2 - Initiator Atomicswap Contract with Participant address

            # Create Atomicswap contract on Initiator chain using Participant address as Redeem Recipient
        print("Here we are")
        init_ctc_cmd = "btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 initiate {} {}".format(response.part_addr, self.init_amount)
        print(init_ctc_cmd)
        init_ctc_json, _, _ = self.execute(init_ctc_cmd)
            # Convert JSON output to Python Object
        print("This is the init_ctc_json" + init_ctc_json)
        init_ctc = json2obj(init_ctc_json)
        print("This is the init_ctc" + init_ctc_json)

            # RPC #2 to Participant, 
            # IF Participant agrees with the Initiator Contract,
            # Returns Participant Contract Redeem Address
        response = stub.ProcessInitiateSwap(atomicswap_pb2.InitiateSwap(init_ctc_redeem_addr=init_ctc.redeemAddr, init_ctc_hex=init_ctc.contractHex, init_ctc_tx_hex=init_ctc.transactionHex, hashed_secret=init_ctc.hashedSecret))

            # Print Step Info
        print_json(2, "Atomicswap Contracts created, waiting until visible", self.step_two_data(init_ctc, response))

            # Waiting for TF Participant contract to be visible
        self.waitUntilTxVisible(response.part_ctc_redeem_addr)


        # Step 3 - Initiator Fulfills Participant Contract with Redeem Transaction, Reveals Secret

            # Make Redeem Transaction

        self.execute("tfchainc atomicswap --encoding json -y redeem {} {}".format(response.part_ctc_redeem_addr, init_ctc.secret))
            
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

    def waitUntilTxVisible(self, hash):
        # Should probably have a max number of tries

        returncode = 1
        while returncode != 0:
            time.sleep(10)
            _, _, returncode = self.execute("tfchainc explore hash "+ hash)



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
