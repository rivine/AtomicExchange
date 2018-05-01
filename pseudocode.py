PartyA (bob) 

initiator_amount = args['my_amount'] #the amount of btc bob will send
acceptor_amount = args['other_amount'] #the amount of rivine alice will receive


initiate_reply = send_initiate(initiator_amount, acceptor_amount)



acceptor_btc_address = initiate_reply.btc_address

btc_atomicswap = `btcatomicswap --testnet --rpcuser=user --rpcpass=pass initiate {{acceptor_btc_address}} {{initiator_amount}}

initiator_wallet_address = `rivinec wallet address`

send_initiate_swap(btc_atomicswap.hash, btc_atomicswap.contract, btc_atomicswap.transaction, initiator_wallet_address)

acceptor_swap_address = receive_accept_swap()

audit_swap = `rivinec atomicswap --testnet audit acceptor_swap_address`

if(audit_swap.amount != acceptor_amount || audit_swap.locktime < 20h || audit_swap.hash != btc_atomicswap.hash || audit_swap.rec_address != initiator_wallet_address):
	send_abort()

#redeem
redeem = `rivinec atomicswap redeem {{acceptor_swap_address}} {{acceptor_amount}} `{{audit_swap.refund_address}} {{initiator_wallet_address}} {{btc_atomicswap.hash}} {{audit_swap.lock_time}} {{btc_atomicswap.secret}}


send_redeem_finished()


PartyB (Alice)


initiator_amount = args['my_amount'] 
acceptor_amount = args['other_amount']

initiate = receive_initiate()

bitcoinaddress = `gentnewaddress "" legacy`

if(initiate.initiator_amount == initiator_amount && initiate.acceptor_amount == acceptor_amount)

	
	send_initiateReply(bitcoinaddress)

initiate_swap = receive_initiate_swap

# audit contract
btc_audit = `btcatomicswap --testnet auditcontract {{initiate_swap.contract}} {{initiate_swap.transaction}}`

if(!btc_audit.locktime.reached > 40h || btc_audit.amount != args['other_amount'] || btc_audit.rec_address != bitcoinaddress):
	send_abort()


rivinec_atomicswap = rivinec atomicswap --testnet participate {{initiate_swap.initiator_wallet}} {{acceptor_amount}} {{initiate_swap.hash}}

initiator_redeem_finished = send_accept_swap(rivinec_atomicswap.OutputID)

get_secret = `rivinec --addr explorer.testnet.threefoldtoken.com extractsecret rivinec_atomicswap.OutputID`

redeem = $ btcatomicswap --testnet --rpcuser=user --rpcpass=pass redeem {{initiate_swap.contract}} {{initiate_swap.transaction}} {{rivinec_atomicswap.OutputID}}
 
