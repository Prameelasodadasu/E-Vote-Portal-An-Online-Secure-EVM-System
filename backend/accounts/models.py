from django.db import models
from django.conf import settings # Import settings to get the User model

class Voter(models.Model):
    # Link to the standard Django User model
    # This is the crucial field that was likely missing or wrong
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voter_profile', # Allows access like user.voter_profile
        null=True, # Allow User to exist without a Voter profile initially
        blank=True # Allow creating Voter in admin without selecting User initially
    )
    voter_uid = models.CharField(max_length=128, unique=True) # Keep your unique ID
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        # Use username from the linked User model if available
        return f"{self.full_name} ({self.user.username if self.user else self.voter_uid})"

# --- We are no longer using OTPToken or AuthToken models ---