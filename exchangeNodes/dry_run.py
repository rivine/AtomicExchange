class AcceptorDryRun:

    initiator_amount = 1
    acceptor_amount = 2

    acceptor_address = "accadr123456789"
    hash = ""
    contract = ""
    transaction = ""
    initiator_wallet_address = ""

    def processCommand(self, command):

        if command.startswith("bitcoin-cli gentnewaddress"):
            print("in new bitcoinaddress")
            print( self.acceptor_address)
            return self.acceptor_address

        if command.startswith("btcatomicswap --testnet auditcontract"):
            return '{\"lockTime\" : \"48\", \"contractValue\" : \"987\", \"recipientAddress\" : \"accadr123456789\"}'
        
        if command.startswith("rivinec atomicswap --testnet participate"):
            return '{\"contractAddress\" : \"contr123456\"}'
        if command.startswith("rivinec --addr explorer.testnet.threefoldtoken.com extractsecret"):
            return '{\"secret\" : \"mys3cr3t\"}'

        if command.startswith("btcatomicswap --testnet --rpcuser=user --rpcpass=pass redeem"):
            return '{\"redeemFee\" : \"0.00002499\", \"redeemTx\" : \"9998\"}'

class InitiatorDryRun:

    def processCommand(self, command):

        if command.startswith("btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate"):
            return "{ \"secret\" : \"12345789\", \"hash\" : \"abc12345678098\", \"contractfee\" : \"0.2\", \"refundfee\" : \"0.1\", \"contract\" : \"54345678\", \"contractTransaction\" : \"tx123456\" }"
        
        if command.startswith("rivinec wallet address"):
            return "099765432"
        if command.startswith("rivinec atomicswap --testnet audit"):
            return '{\"contractValue\" : \"1234\", \"lockTime\" : \"23\", \"hash\" : \"abc12345678098\", \"recipientAddress\" : \"099765432\", \"refundAddress\" : \"7777888\" }'

        if command.startswith("rivinec atomicswap redeem"):
            return '{\"redeemFee\" : \"0.00002499\", \"redeemTx\" : \"9918\"}'