
from concurrent import futures
import time
import sys

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc

import urllib2

import os
from optparse import OptionParser
import json
from collections import namedtuple

from dry_run import ParticipantDryRun
def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)



_ONE_DAY_IN_SECONDS = 60 * 60 * 24

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

class AtomicSwap(atomicswap_pb2_grpc.AtomicSwapServicer):

    dry_run = False
    init_amount = 0
    part_amount = 0

    def __init__(self, init_amount, part_amount, dry_run):

        self.init_amount = init_amount
        self.part_amount = part_amount

        self.dry_run = dry_run

    def execute(self, process):

        if self.dry_run:
            dry = ParticipantDryRun(init_amount, part_amount)
            return dry.processCommand(process)

        process = os.popen(process)
        output = reprocessed = process.read()
        process.close()
        
        return output.rstrip()

    def ProcessInitiate(self, request, context):

        #######GLOSSARY######
        # init = initiator
        # part = participant
        # ctc = contract
        # tx = transaction
        # addr = address
        #####################

        # Step 1 - Initiate Request received, Confirming amounts, exchanging recipient addresses for Contracts

            # Generating Participant Address on Initiator chain
        self.part_addr = self.execute('bitcoin-cli getnewaddress \"\" legacy')

            # Saving Initiator Address for Contract creation step
        print(request.init_addr)
        self.init_addr = request.init_addr

            # Print Step info to UI
        print_json(1, "Sent Atomicswap request confirmation with Participant Address", self.step_one_data(request))

            # RPC response to Initiate Request
            # Returns Participant Address
        return atomicswap_pb2.InitiateReply(part_addr=self.part_addr)

    def ProcessInitiateSwap(self, request, context):

        # Step 2 - Initiator Contract details received, Auditing it

        #    # Run Audit command
        # part_ctc_audit_json =  self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 auditcontract {} {}".format(request.contractHex, request.transactionHex)) 
        # part_ctc_audit = json2obj(part_ctc_audit_json)

        # if all(part_ctc_audit.verifications.values):
        #    print("Initiator Contract Audit Successful")
        # else:
        #    print("Initiator Contract Audit Failed")
        #    exit(1)

            # Saving Initiator Contract and Transaction hexstrings for Redeem Step
        self.init_ctc_hex = request.init_ctc_hex
        self.init_ctc_tx_hex = request.init_ctc_tx_hex
        self.init_ctc_redeem_addr = request.init_ctc_redeem_addr

        print(self.init_addr)
        print(self.part_amount)
        print(request.hashed_secret)

            # Create Atomicswap Contract on Participant chain using Initiator Address as Redeem Recipient
        part_ctc_json = self.execute("tfchainc atomicswap --encoding json -y participate {} {} {}".format(self.init_addr, self.part_amount, request.hashed_secret))
        part_ctc = json2obj(part_ctc_json)

            # Print Step info to UI
        print_json(2, "Saved Initiator Contract Details and Created Participant Contract", self.step_two_data(request, part_ctc))

            # RPC response to Create Contract request
            # Returns Participant Contract Redeem Address
        return atomicswap_pb2.AcceptSwap(part_ctc_redeem_addr=part_ctc.outputid)


    def ProcessRedeemed(self,request,context):

        # Step 3 - Initiator has revealed Secret, Redeeming Initiator Contract
            
            # Wait until contract is revealed
        self.waitUntilTxVisible(self.init_ctc_redeem_addr)

            # Make Redeem Transaction
        self.execute("btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 redeem {} {} {}".format(self.init_ctc_hex, self.init_ctc_tx_hex, request.secret))

            # Print Step Info to UI
        print_json(3, "Created Redeemed Transaction, Finished Participant Flow", self.step_three_data())

            # RPC response to Redeem Finished message
            # Returns Finished message
        return atomicswap_pb2.ParticipantRedeemFinished(finished=True)


    #########################
    # r = request
    # pc = part_ctc
    #########################

    def step_one_data(self, r):
        data = {}
        data['participantAmount'] = r.part_amount
        data['initiatorAmount'] = r.init_amount
        data['participantAddress'] = self.part_addr
        data['initiatorAddress'] = self.init_addr
        return data

    def step_two_data(self, r, pc):
        data = {}
        data['initiatorContractHex'] = r.init_ctc_hex
        data['initiatorContractTransactionHex'] = r.init_ctc_tx_hex
        data['initiatorContractRedeemAddress'] = r.init_ctc_redeem_addr
        data['hashedSecret'] = r.hashed_secret
        data['participantContractRedeemAddress'] = pc.outputid
        return data

    def step_three_data(self):
        data = {}
        data['finished'] = "true"
        return data

    def waitUntilTxVisible(self, hash):
        while True:
            try:
                btc_tx_json = urllib2.urlopen("https://test-insight.bitpay.com/api/addr/"+ hash).read()
                btc_tx = json2obj(btc_tx_json)
                print("txApperances(it's appeArances btw...): " + str(btc_tx.txApperances))
                if btc_tx.txApperances > 0:
                    break
            except Exception as e:
                print(e, 'Trying again in 10 seconds...')
                time.sleep(10)
        


def serve(init_amount, part_amount, dry_run):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atomicswap_pb2_grpc.add_AtomicSwapServicer_to_server(AtomicSwap(init_amount, part_amount, dry_run), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)



if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-m", "--my-amount", dest="part_amount",
                    help="Your amount of your currency to swap", metavar="INITIATORAMOUNT")

    parser.add_option("-o", "--other-amount",
                    dest="init_amount", default=True,
                    help="The amount of the other partners currency to swap")
    
    parser.add_option("-d", "--dry-run", action="store_true",
                        dest="dry_run",  help="Do a dry run with dummy data")

    (options, args) = parser.parse_args()
    
    init_amount = options.init_amount
    part_amount = options.part_amount

    dry_run = options.dry_run

    serve(init_amount, part_amount, dry_run)
