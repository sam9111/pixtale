import os
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scopes = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

creds = None

if os.path.exists("_secrets_/token.json"):
    creds = Credentials.from_authorized_user_file("_secrets_/token.json", scopes)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "_secrets_/client_secret.json", scopes
        )
        creds = flow.run_local_server()
    print(creds)
    # Save the credentials for the next run
    with open("_secrets_/token.json", "w") as token:
        token.write(creds.to_json())

from google.auth.transport.requests import AuthorizedSession

authed_session = AuthorizedSession(creds)


response = authed_session.get(
    "https://photoslibrary.googleapis.com/v1/albums",
    headers={"content-type": "application/json"},
)

response.json()


response = authed_session.get(
    "https://photoslibrary.googleapis.com/v1/albums",
    headers={"content-type": "application/json"},
)

response.json()
