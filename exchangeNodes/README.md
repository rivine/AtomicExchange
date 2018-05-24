# install
- install npm
- install python


```sh
apt-get install pip
pip install grpcio
pip install grpcio-tools
make
```

# Run acceptor

values are currently hard coded, use these values. 

```sh
python acceptor.py -m 1234 -o 987 -d
```

# Run initiator

values are currently hard coded, use these values. 

```sh
python initiator.py -m 987 -o 1234 -d
```

# Output

## Initiator - Bob

```sh
{"step" : 1, "stepName" : "initiateExchange" , data: { "initiatorAmount" : "8", acceptorAmount: 10 }}
{ "step" : 2, "stepName": "reveiveAddress" : data: {"address": "ghjkllm"}
{ "step" : 3, "stepName" : "createSmartContractInitiator,
	data: {"hash": "ghjkllm"
		"contractValue: "20"
		"contract: "1234"
		"contractTransaction: "1234"
		"hash": "6qsdfaq65f4a"
		"recipientAddress": "mazief58amzf41"

	}
{ "step" : 4, "stepName" : "generateInitiatorWalletAddress" , data: { "address": "sefzqfzara5142q63z5f4"}}
{ "step" : 5, "stepName" : "sendSmartContractInitiator" ,
	data: {"hash": "ghjkllm"
		"contractValue: "20"
		"contract: "1234"
		"contractTransaction: "1234"
		"hash": "6qsdfaq65f4a"
		"recipientAddress": "mazief58amzf41"
		"generateInitiatorWalletAddress: "fmaf4f5qsfa654"
	}
}
{ "step" : 6, "stepName" : "auditSmartContractAcceptor" ,
	data: { 
		contractValue: {
			expected:  "acceptorAmount"
			actual: contractValue
		}
		lockTime: {
			expected:  ">40"
			actual: 20
		}	
		hash: {
			expected:  atomicSwapHash
			actual: auditSwapHash
		}
		address: {
			expected:  initiatorWalletAddress
			actual: receipientAddress
		}
		contractValid: false;
	}
}
{ "step" : 7, "stepName" : "redeemFundsInitiator" ,	
	data: {
		"acceptorSwapAddress": "ghjkllm"
		"acceptorAmount: "20"
		"refundAddress: "6qsdfaq65f4a"
		"initiatorWalletAddress: "6qsdfaq65f4a"
		"hash": "6qsdfaq65f4a"
		"lockTime": "mazief58amzf41"
		"secret: "fmaf4f5qsfa654"
	}
}
{ "step" : 8, "stepName" : "redeemInitiatorFinished"}
```

## Acceptor - Alice

```sh
{ "step" : 1, "stepName" : "initiateReceived , data: { "initiatorAmount" : "8", acceptorAmount: 10 }}
{ "step" : 2, "stepName" : "generateAddress" , data: {"address": "ghjkllm"}}
{ "step" : 3, "stepName" : "sendAddress" , data: {"address": "ghjkllm"}}
{ "step" : 4, "stepName" : "receiveSmartContractInitiator" , 	
	data: {"hash": "ghjkllm"
		"contractValue: "20"
		"contract: "1234"
		"contractTransaction: "1234"
		"hash": "6qsdfaq65f4a"
		"recipientAddress": "mazief58amzf41"
		"generateInitiatorWalletAddress: "fmaf4f5qsfa654"
	}
{ "step" : 5, "stepName" : "auditSmartContractInitiator" , 
	data: {
		locktime: {
			expected:  ">40"
			actual: 20
		}	
		amount: {
			expected:  initiatorAmount
			actual: contractValue
		}
		address: {
			expected:  bitcoinAddress
			actual: recipientAddress
		}
		contractValid: false;
	}
}
{ "step" : 6, "stepName" : createSmartContractAcceptor , 
	data: {"hash": "ghjkllm"
		"contractValue: "20"
		"contract: "1234"
		"contractTransaction: "1234"
		"hash": "6qsdfaq65f4a"
		"recipientAddress": "mazief58amzf41"
		"generateInitiatorWalletAddress: "fmaf4f5qsfa654"
	}
}
{ "step" : 7, "stepName" : sendSmartContractAcceptor , 
	data: {"hash": "ghjkllm"
		"contractValue: "20"
		"contract: "1234"
		"contractTransaction: "1234"
		"hash": "6qsdfaq65f4a"
		"recipientAddress": "mazief58amzf41"
		"generateInitiatorWalletAddress: "fmaf4f5qsfa654"
	}
}
{ "step" : 8, "stepName" : "redeemFundsAcceptor" ,	data: {
		"initiatorContract": "ghjkllm"
		"initiatorTransaction: "20"
		"secret: "6qsdfaq65f4a"
	}
}
{ "step" : 9, "stepName" : "redeemAcceptorFinished"}
```