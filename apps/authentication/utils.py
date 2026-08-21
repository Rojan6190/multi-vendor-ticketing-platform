from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from django.conf import settings


def verify_google_token(token):
    """Verifies a Google id_token against Google's servers. Returns the payload (sub, email, name) or None."""
    try:
        return google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        return None


"""
User clicks "Login with Google"
          ↓
Google authenticates user
          ↓
Google gives your app an ID token
          ↓
verify_google_token(token)
          ↓
Google verifies the token
          ↓
You get trusted user information
    
"""