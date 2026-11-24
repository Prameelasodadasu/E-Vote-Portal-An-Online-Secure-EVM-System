from django.db import models

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')],
        default='draft'
    )

    def __str__(self):
        return self.title

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=120)
    party = models.CharField(max_length=120, blank=True)
    symbol = models.CharField(max_length=80, blank=True)  # like "Lotus" or "Hand"

    def __str__(self):
        return f"{self.name} - {self.party}"


