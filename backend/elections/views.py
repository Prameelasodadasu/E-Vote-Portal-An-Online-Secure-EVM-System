# DRF imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Model imports
from .models import Election, Candidate
from voting.models import EncryptedVote
from accounts.models import Voter
from audit.models import AuditLog

# Util imports
from voting.utils import encrypt_vote, decrypt_vote

# Serializer imports
try:
    from .serializers import ElectionSerializer
except ImportError:
    class ElectionSerializer:
        def __init__(self, *args, **kwargs): pass
        @property
        def data(self): return {"error": "Serializer not defined"}

# Other imports
from django.utils import timezone
from django.shortcuts import get_object_or_404
from collections import Counter
from django.conf import settings
from web3 import Web3
import json
import csv
import os
from datetime import datetime # For parsing timestamps

# --- Blockchain Setup (Helper function) ---
def get_vote_ledger_contract():
    """Connects to Ganache and loads the VoteLedger contract."""
    try:
        w3 = Web3(Web3.HTTPProvider(settings.GANACHE_URL))
        if not w3.is_connected():
            print("ERROR: Failed to connect to Ganache RPC.")
            return None, None
        contract_address = settings.VOTE_LEDGER_CONTRACT_ADDRESS
        contract_abi = json.loads(settings.VOTE_LEDGER_CONTRACT_ABI)
        checksum_address = Web3.to_checksum_address(contract_address)
        contract = w3.eth.contract(address=checksum_address, abi=contract_abi)
        return w3, contract
    except Exception as e:
        print(f"ERROR setting up blockchain connection: {e}")
        return None, None

# --- Data Logging Setup ---
LOG_FILE_PATH = os.path.join(settings.BASE_DIR.parent, 'data', 'vote_log.csv') # Assumes 'data' folder is outside 'backend'

def log_vote_to_csv(timestamp, election_id, candidate_id, voter_hash):
    """Appends vote data to the CSV log file."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        file_exists = os.path.isfile(LOG_FILE_PATH)
        with open(LOG_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists or os.path.getsize(LOG_FILE_PATH) == 0:
                writer.writerow(['Timestamp', 'ElectionID', 'CandidateID', 'VoterHash'])
            writer.writerow([timestamp.isoformat(), election_id, candidate_id, voter_hash])
        print(f"--- Logged vote to CSV: {timestamp}, E:{election_id}, C:{candidate_id}, V:{voter_hash[:8]}... ---")
    except Exception as e:
        print(f"ERROR: Failed to log vote to CSV: {e}")
# --- End Data Logging Setup ---


@api_view(['GET'])
def active_elections(request):
    """ Lists active elections """
    now = timezone.now()
    try:
        elections = Election.objects.filter(
            status='active', starts_at__lte=now, ends_at__gte=now
        )
        serializer = ElectionSerializer(elections, many=True)
        return Response(serializer.data)
    except Exception as e:
        print(f"Error in active_elections: {e}")
        return Response({"error": f"Could not retrieve elections: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def tally_results(request, election_id):
    """ Counts the DECRYPTED votes for a specific election. """
    
    log_who = "AnonymousUser"
    if request.user and request.user.is_authenticated:
        log_who = request.user.username
    
    try:
        election = get_object_or_404(Election, id=election_id)
    except Election.DoesNotExist:
        AuditLog.objects.create(who=log_who, action="TALLY_ACCESS_FAIL", meta={"election_id": election_id, "reason": "Election not found"})
        return Response({"error": "Election not found"}, status=status.HTTP_404_NOT_FOUND)

    # --- *** KEY CHANGE: Comment out this check for the demo *** ---
    # now = timezone.now()
    # if election.status != 'closed' and election.ends_at > now:
    #     AuditLog.objects.create(who=log_who, action="TALLY_ACCESS_FAIL", meta={"election_id": election_id, "reason": "Election not closed"})
    #     return Response({"error": "Election is not closed yet"}, status=status.HTTP_400_BAD_REQUEST)
    # ---

    encrypted_votes = EncryptedVote.objects.filter(election=election)
    candidate_counts = Counter()
    successful_decryptions = 0
    failed_decryptions = 0

    for vote in encrypted_votes:
        try:
            if vote.ciphertext_b64:
                decrypted_candidate_id = decrypt_vote(vote.ciphertext_b64)
                candidate_counts[decrypted_candidate_id] += 1
                successful_decryptions += 1
            else:
                print(f"Warning: Vote ID {vote.id} has no ciphertext to decrypt.")
                failed_decryptions += 1
        except ValueError as e:
            print(f"Failed to decrypt vote ID {vote.id}: {e}")
            failed_decryptions += 1

    results = []
    candidates = Candidate.objects.filter(election=election)
    for candidate in candidates:
        candidate_id_str = str(candidate.id)
        vote_count = candidate_counts.get(candidate_id_str, 0)
        results.append({
            "candidate_id": candidate.id, "name": candidate.name,
            "party": candidate.party, "symbol": candidate.symbol,
            "votes": vote_count
        })

    AuditLog.objects.create(
        who=log_who, 
        action="TALLY_ACCESS_SUCCESS",
        meta={"election_id": election_id, "election_title": election.title}
    )

    return Response({
        "election": election.title,
        "total_votes_counted": successful_decryptions,
        "invalid_or_undecryptable_votes": failed_decryptions,
        "results": results
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_vote(request, election_id):
    """ Casts a secure, ENCRYPTED vote, logs data, and records hash on Blockchain """

    user = request.user
    log_who = user.username

    try:
        voter = user.voter_profile
    except Voter.DoesNotExist:
         AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "reason": "No voter profile"})
         return Response({"error": "Authenticated user does not have a linked Voter profile."}, status=status.HTTP_403_FORBIDDEN)

    if voter.has_voted:
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "reason": "Already voted"})
        return Response({"error": "You have already voted"}, status=status.HTTP_403_FORBIDDEN)

    now = timezone.now()
    try:
        election = Election.objects.get(
            id=election_id, status='active',
            starts_at__lte=now, ends_at__gte=now
        )
    except Election.DoesNotExist:
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "reason": "Election not found/active"})
        return Response({"error": "Election not found or not active"}, status=status.HTTP_4AF_NOT_FOUND)

    candidate_id = request.data.get("candidate_id")
    if not candidate_id:
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "reason": "Candidate ID missing"})
        return Response({"error": "Candidate ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        candidate = Candidate.objects.get(id=candidate_id, election=election)
    except Candidate.DoesNotExist:
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "candidate_id": candidate_id, "reason": "Invalid candidate"})
        return Response({"error": "Invalid candidate for this election"}, status=status.HTTP_400_BAD_REQUEST)

    # --- AI Anomaly Detection ---
    vote_timestamp = timezone.now()
    ANOMALY_THRESHOLD_SECONDS = 2
    try:
        if os.path.exists(LOG_FILE_PATH) and os.path.getsize(LOG_FILE_PATH) > 50:
            with open(LOG_FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                try:
                    header = next(reader)
                    last_vote_row = None
                    for row in reader:
                        last_vote_row = row
                    
                    if last_vote_row:
                        last_vote_timestamp_str = last_vote_row[0]
                        last_vote_time = datetime.fromisoformat(last_vote_timestamp_str)
                        time_diff = vote_timestamp - last_vote_time
                        
                        if time_diff.total_seconds() < ANOMALY_THRESHOLD_SECONDS:
                            print(f"--- ANOMALY DETECTED: Rapid vote attempt by {log_who}. Time diff: {time_diff.total_seconds()}s ---")
                            AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"reason": "Anomaly detected: rapid voting"})
                            return Response({"error": "Anomaly detected. Please wait a moment and try again."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                except (StopIteration, IndexError, csv.Error) as e:
                    print(f"Note: Could not read last vote from log for anomaly check: {e}")
    except Exception as e:
        print(f"ERROR during anomaly check: {e}") 
        AuditLog.objects.create(who="SYSTEM", action="ANOMALY_CHECK_ERROR", meta={"error": str(e)})
    # --- End Anomaly Detection ---

    # Log vote data to CSV
    log_vote_to_csv(vote_timestamp, election.id, candidate.id, voter.voter_uid)

    try:
        encrypted_candidate_id_str = encrypt_vote(str(candidate_id))
    except Exception as e:
        print(f"Error encrypting vote: {e}")
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "candidate_id": candidate_id, "reason": "Encryption error"})
        return Response({"error": "Failed to encrypt vote data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Blockchain Interaction ---
    w3, contract = get_vote_ledger_contract()
    tx_hash_hex = None
    if w3 and contract:
        try:
            account = w3.eth.accounts[0]
            tx_hash = contract.functions.recordVote(
                election.id, voter.voter_uid
            ).transact({'from': account})
            tx_hash_hex = tx_hash.hex()
            print(f"--- Blockchain transaction sent: {tx_hash_hex} ---")
        except Exception as e:
            print(f"ERROR: Failed to send blockchain transaction: {e}")
            tx_hash_hex = None
    else:
        print("WARNING: Could not connect to blockchain. Skipping blockchain record.")
    # --- End Blockchain Interaction ---

    # --- Save the ENCRYPTED vote to DB ---
    try:
        EncryptedVote.objects.create(
            election=election, candidate=candidate,
            voter_hash=voter.voter_uid,
            ciphertext_b64=encrypted_candidate_id_str,
            tx_hash=tx_hash_hex
        )
    except Exception as e:
        print(f"Error saving encrypted vote to DB: {e}")
        AuditLog.objects.create(who=log_who, action="VOTE_CAST_FAIL", meta={"election_id": election_id, "candidate_id": candidate_id, "reason": "DB save error"})
        return Response({"error": "Could not save encrypted vote."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # ---

    # Mark voter as having voted
    voter.has_voted = True
    voter.save()

    # Invalidate the DRF token by deleting it
    try:
        request.auth.delete()
    except Exception as e:
        print(f"Error deleting DRF token: {e}")

    # Log successful vote
    AuditLog.objects.create(
        who=log_who, action="VOTE_CAST_SUCCESS",
        meta={"election_id": election_id, "candidate_id": candidate_id, "tx_hash": tx_hash_hex}
    )

    return Response(
        {"message": f"Vote cast successfully (Encrypted) for {candidate.name}. TxHash: {tx_hash_hex or 'N/A'}"},
        status=status.HTTP_201_CREATED
    )

# -------------------------------------
# VIEW: Verify Blockchain Log
# -------------------------------------
@api_view(['GET'])
def verify_blockchain_log(request):
    """ Reads VoteRecorded events from the VoteLedger smart contract. """
    w3, contract = get_vote_ledger_contract()
    if not w3 or not contract:
        return Response({"error": "Could not connect to blockchain node."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        event_filter = contract.events.VoteRecorded.create_filter(from_block=0)
        logs = event_filter.get_all_entries()
        formatted_logs = []
        for log in logs:
            voter_hash_data = log['args']['voterHash']
            voter_hash_str = ""
            if isinstance(voter_hash_data, bytes):
                voter_hash_str = voter_hash_data.hex()
            else:
                voter_hash_str = str(voter_hash_data)

            formatted_logs.append({
                'blockNumber': log['blockNumber'],
                'transactionHash': log['transactionHash'].hex(),
                'electionId': log['args']['electionId'],
                'voterHash': voter_hash_str,
            })
            
        return Response({
            "contract_address": settings.VOTE_LEDGER_CONTRACT_ADDRESS,
            "total_events": len(formatted_logs),
            "events": formatted_logs
        })

    except Exception as e:
        print(f"ERROR reading blockchain events: {e}")
        return Response({"error": f"Failed to retrieve blockchain logs: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)