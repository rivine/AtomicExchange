import json 


class AcceptorDryRun:
    initiator_amount = 0
    acceptor_amount = 0

    def __init__(self, initiator_amount, acceptor_amount):
        self.initiator_amount = initiator_amount
        self.acceptor_amount = acceptor_amount

  

    acceptor_address = "accadr123456789"
    hash = ""
    contract = ""
    transaction = ""
    initiator_wallet_address = ""

    def processCommand(self, command):

        if command.startswith("bitcoin-cli gentnewaddress"):
            return self.acceptor_address

        if command.startswith("btcatomicswap --testnet auditcontract"):

            data = {}
            data['lockTime'] = 48
            data['contractValue'] = self.initiator_amount
            data['recipientAddress'] = "accadr123456789" #todo gen
            json_data = json.dumps(data)

            return json_data
         

        if command.startswith("rivinec atomicswap --testnet participate"):

            data = {}
            data["contractAddress"] = "contr123456"
            json_data = json.dumps(data)

            return json_data

        if command.startswith("rivinec --addr explorer.testnet.threefoldtoken.com extractsecret"):

            data = {}
            data["secret"] = "mys3cr3t"
            json_data = json.dumps(data)

            return json_data

        if command.startswith("btcatomicswap --testnet --rpcuser=user --rpcpass=pass redeem"):

            data = {}
            data["redeemFee"] = "0.00002499"
            data["redeemTx"] = "9998"
            json_data = json.dumps(data)
            
            return json_data
            

class InitiatorDryRun:

    initiator_amount = 0
    acceptor_amount = 0

    def __init__(self, initiator_amount, acceptor_amount):
        self.initiator_amount = initiator_amount
        self.acceptor_amount = acceptor_amount


    def processCommand(self, command):

        if command.startswith("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate"):
            return "{ \"secret\" : \"12345789\", \"hash\" : \"abc12345678098\", \"contractfee\" : \"0.2\", \"refundfee\" : \"0.1\", \"contract\" : \"54345678\", \"contractTransaction\" : \"tx123456\" }"
        
        if command.startswith("rivinec wallet address"):
            return "099765432"

        if command.startswith("rivinec atomicswap --testnet audit"):
            data = {}
            data["contractValue"] = self.acceptor_amount
            data["lockTime"] = 23
            data["hash"] = "abc12345678098"
            data["recipientAddress"] = "099765432"
            data["refundAddress"] = "7777888"
            return json.dumps(data)
            

        if command.startswith("rivinec atomicswap redeem"):
            return '{\"redeemFee\" : \"0.00002499\", \"redeemTx\" : \"9918\"}'