from django.db import models
from elections.models import Election, Candidate  # <-- Make sure Candidate is imported

class EncryptedVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True) # <-- ADD THIS LINE
    voter_hash = models.CharField(max_length=128, blank=True)
    ciphertext_b64 = models.TextField(blank=True)
    cast_at = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Vote {self.id} for election {self.election_id}"

