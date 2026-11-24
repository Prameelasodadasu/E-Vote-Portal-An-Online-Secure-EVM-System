from rest_framework import serializers
from .models import Election, Candidate

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'party', 'symbol']

class ElectionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'starts_at', 'ends_at', 'status', 'candidates']