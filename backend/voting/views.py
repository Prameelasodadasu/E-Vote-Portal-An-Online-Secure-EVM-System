from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import EncryptedVote
from .serializers import EncryptedVoteSerializer
from elections.models import Election
from accounts.models import Voter
import hashlib
from .utils import hash_voter_id, encrypt_vote  

@api_view(['POST'])
def cast_vote(request):
    voter_uid = request.data.get("voter_uid")   # raw voter ID
    candidate_id = str(request.data.get("candidate_id"))  # candidate choice
    election_id = request.data.get("election")

    if not voter_uid or not candidate_id or not election_id:
        return Response({"error": "Missing fields"}, status=400)

    # ✅ Step 1: Hash voter ID
    voter_hash = hash_voter_id(voter_uid)

    # ✅ Step 2: Encrypt candidate choice
    ciphertext = encrypt_vote(candidate_id)

    # ✅ Step 3: Save encrypted vote in DB
    vote = EncryptedVote.objects.create(
        election_id=election_id,
        voter_hash=voter_hash,
        ciphertext_b64=ciphertext
    )

    return Response(
        {"message": "Vote cast successfully!", "vote_id": vote.id},
        status=status.HTTP_201_CREATED
    )
