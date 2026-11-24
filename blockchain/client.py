import os
import json
from web3 import Web3

# Connect to local Ganache blockchain
GANACHE_URL = "http://127.0.0.1:7545"  # Check Ganache for the correct port
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("⚠️ Could not connect to Ganache. Make sure it's running!")

# Paste your contract address here (from Remix deployment)
CONTRACT_ADDRESS = w3.to_checksum_address("0x8a0411D9abBBAC6082E1a93BC08b860992FB71a9")

# Paste your contract ABI here (replace the [...] with actual ABI JSON)
ABI = [
    # 👇 Paste your ABI JSON array here[
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_electionId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_voterHash",
				"type": "string"
			}
		],
		"name": "recordVote",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "electionId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "string",
				"name": "voterHash",
				"type": "string"
			}
		],
		"name": "VoteRecorded",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]


# Create a contract instance
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Pick a Ganache account for sending transactions (the owner/deployer)
ACCOUNT_ADDRESS = w3.eth.accounts[0]
PRIVATE_KEY = "0x070794eae67e1c09a7870a9bfbd11f33ef97dffcafb116f94b353f9890a75927"  # Get it from Ganache -> key icon

def cast_vote(candidate_id):
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)

    # Build transaction
    txn = contract.functions.vote(candidate_id).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.to_wei('1', 'gwei'),
    })

    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt
