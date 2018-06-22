import json

class InitiatorDryRun:

    init_amount = 0
    part_amount = 0

    def __init__(self, init_amount, part_amount):
        self.init_amount = init_amount
        self.part_amount = part_amount

    def processCommand(self, command):
        if command.startswith("btcatomicswap --testnet --rpcuser=user --rpcpass=pass -s localhost:8332 initiate"):
            return "{ \"secret\" : \"12345789\", \"hashed_secret\" : \"examplehashedsecret\", \"ctc_hex\" : \"v3ry10n6h3x5tr1n6\", \"tx_hex\" : \"3v3n10n63rh3x5tr1n6\", \"redeem_addr\" : \"btcRedeemAddrEx\" }"
        
        if command.startswith("tfchainc wallet address"):
            return "Created new address: tfaccadr123456789"            

class ParticipantDryRun:
    init_amount = 0
    part_amount = 0

    def __init__(self, init_amount, part_amount):
        self.init_amount = init_amount
        self.part_amount = part_amount

    part_addr = "btcaccadr123456789"

    def processCommand(self, command):

        if command.startswith("bitcoin-cli getnewaddress"):
            return self.part_addr         

        if command.startswith("tfchainc atomicswap participate"):

            data = {}
            data["redeem_addr"] = "tfRedeemAddrEx"
            json_data = json.dumps(data)

            return json_data
            

