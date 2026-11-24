from django.db import models

class AuditLog(models.Model):
    who = models.CharField(max_length=128)   # Voter ID or 'system'
    action = models.CharField(max_length=128)
    meta = models.JSONField(default=dict, blank=True)
    at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.at} - {self.who} - {self.action}"
