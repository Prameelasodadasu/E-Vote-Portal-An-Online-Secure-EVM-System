from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Voter
from audit.models import AuditLog
import random
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings

# --- Import SMS Library ---
from twilio.rest import Client
# --------------------------

User = get_user_model()

temp_otp_storage = {}
temp_otp_timestamps = {}

@api_view(['POST'])
def request_otp(request):
    voter_uid = request.data.get('voter_uid')
    # Delivery method is now implicitly SMS

    if not voter_uid:
        return Response({"error": "voter_uid is required"}, status=status.HTTP_400_BAD_REQUEST)

    # --- Find User and Voter (Improved Logic) ---
    user = None
    voter = None
    try:
        voter = Voter.objects.select_related('user').get(voter_uid=voter_uid)
        user = voter.user
    except Voter.DoesNotExist:
        try:
            user = User.objects.get(username=voter_uid)
            voter, created = Voter.objects.get_or_create(user=user, defaults={'voter_uid': voter_uid, 'full_name': user.get_full_name() or user.username})
        except User.DoesNotExist:
             AuditLog.objects.create(who=f"UID:{voter_uid}", action="OTP_REQUEST_FAIL", meta={"reason": "User/Voter not found"})
             return Response({"error": "Neither Voter profile nor User account found for this ID."}, status=status.HTTP_404_NOT_FOUND)
    if voter and not user: # Link if possible
         try:
             user = User.objects.get(username=voter_uid)
             voter.user = user; voter.save()
         except User.DoesNotExist:
              AuditLog.objects.create(who=f"UID:{voter_uid}", action="OTP_REQUEST_FAIL", meta={"reason": "Voter exists, no matching User"})
              return Response({"error": "Voter profile exists, but no matching Django User account found to link."}, status=status.HTTP_404_NOT_FOUND)
    if not user:
         AuditLog.objects.create(who=f"UID:{voter_uid}", action="OTP_REQUEST_FAIL", meta={"reason": "Could not identify user"})
         return Response({"error": "Could not identify associated user account."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    voter = getattr(user, 'voter_profile', voter) # Ensure voter is assigned
    if not voter:
         AuditLog.objects.create(who=user.username, action="OTP_REQUEST_FAIL", meta={"reason": "Voter profile missing"})
         return Response({"error": "Voter profile missing for user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if voter.has_voted:
        AuditLog.objects.create(who=user.username, action="OTP_REQUEST_FAIL", meta={"reason": "Already voted"})
        return Response({"error": "This voter has already voted"}, status=status.HTTP_403_FORBIDDEN)
    # --- End User/Voter Find ---

    # Check phone number
    if not voter.phone:
        AuditLog.objects.create(who=user.username, action="OTP_REQUEST_FAIL", meta={"reason": "Phone missing"})
        return Response({"error": "No phone number registered for this voter."}, status=status.HTTP_400_BAD_REQUEST)
    recipient_address = voter.phone

    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    temp_otp_storage[voter_uid] = otp_code
    temp_otp_timestamps[voter_uid] = timezone.now()
    print(f"--- OTP for {user.username} (VoterUID: {voter_uid}): {otp_code} ---") # Keep for debugging

    # --- Send OTP via SMS using Twilio ---
    message_sent = False
    error_message = None
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_body = f"Your E-Voting Portal OTP is: {otp_code}"
        # Ensure phone is in E.164 format (e.g., +91...)
        to_phone_number = recipient_address
        if not to_phone_number.startswith('+'):
             print(f"Warning: Phone number {to_phone_number} missing country code prefix (+). Attempting to send anyway.")
             # Add more robust formatting if needed based on Twilio requirements

        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        if message.sid:
            message_sent = True
            AuditLog.objects.create(who=user.username, action="OTP_SMS_SENT_SUCCESS", meta={"to_phone": recipient_address, "sid": message.sid})
        else:
            error_message = "Twilio failed to return message SID."
            AuditLog.objects.create(who=user.username, action="OTP_SMS_SENT_FAIL", meta={"error": error_message})
    except Exception as e:
        error_message = f"Failed to send SMS via Twilio: {e}"
        print(f"ERROR: {error_message}")
        AuditLog.objects.create(who=user.username, action="OTP_SMS_SENT_FAIL", meta={"error": str(e)})
    # --- End SMS Sending ---

    # --- Handle outcome ---
    if message_sent:
        AuditLog.objects.create(who=user.username, action="OTP_REQUEST_SUCCESS", meta={"voter_uid": voter_uid, "method": "SMS"})
        return Response({"message": "OTP has been sent via SMS (check console for testing)."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to send OTP via SMS. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- verify_otp function remains the same ---
@api_view(['POST'])
def verify_otp(request):
    voter_uid = request.data.get('voter_uid')
    otp_code = request.data.get('otp_code')

    if not voter_uid or not otp_code:
        return Response({"error": "voter_uid and otp_code are required"}, status=status.HTTP_400_BAD_REQUEST)

    stored_otp = temp_otp_storage.get(voter_uid)
    otp_time = temp_otp_timestamps.get(voter_uid)
    log_who = f"UID:{voter_uid}"

    if not stored_otp or not otp_time:
        AuditLog.objects.create(who=log_who, action="OTP_VERIFY_FAIL", meta={"reason": "OTP not found/expired temp"})
        return Response({"error": "No OTP found or it expired (in-memory storage)"}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now() > otp_time + timezone.timedelta(minutes=5):
         if voter_uid in temp_otp_storage: del temp_otp_storage[voter_uid]
         if voter_uid in temp_otp_timestamps: del temp_otp_timestamps[voter_uid]
         AuditLog.objects.create(who=log_who, action="OTP_VERIFY_FAIL", meta={"reason": "OTP expired"})
         return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

    if otp_code != stored_otp:
        AuditLog.objects.create(who=log_who, action="OTP_VERIFY_FAIL", meta={"reason": "Invalid OTP code"})
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    if voter_uid in temp_otp_storage: del temp_otp_storage[voter_uid]
    if voter_uid in temp_otp_timestamps: del temp_otp_timestamps[voter_uid]

    user = None
    try:
        voter = Voter.objects.select_related('user').get(voter_uid=voter_uid)
        user = voter.user
    except Voter.DoesNotExist:
        try:
            user = User.objects.get(username=voter_uid)
        except User.DoesNotExist:
            pass

    if not user:
         AuditLog.objects.create(who=log_who, action="OTP_VERIFY_FAIL", meta={"reason": "User not found after valid OTP"})
         return Response({"error": "Could not find associated user account after OTP verification."}, status=status.HTTP_404_NOT_FOUND)
    log_who = user.username

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    print(f"--- DEBUG: DRF Token created/retrieved for user '{user.username}'. Key: {token.key} ---")
    AuditLog.objects.create(who=log_who, action="OTP_VERIFY_SUCCESS")

    return Response({
        "message": "OTP verified successfully.",
        "token": token.key
    }, status=status.HTTP_200_OK)