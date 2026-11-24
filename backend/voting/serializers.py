from rest_framework import serializers
from .models import EncryptedVote

class EncryptedVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedVote
        fields = ['id', 'election', 'voter_hash', 'ciphertext_b64', 'cast_at', 'tx_hash']

