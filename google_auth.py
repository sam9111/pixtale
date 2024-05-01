from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import requests


TOKEN_FILE = "_secrets_/token.json"
CLIENT_SECRET_FILE = "_secrets_/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def download_mediaitem(media_item, download_folder):
    """Download a photo from its URL."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    if media_item["mimeType"] == "video/mp4":
        download_url = (
            media_item["baseUrl"] + "=dv"
        )  # This might need to be adjusted based on Google Photos API
    else:
        download_url = media_item["baseUrl"] + "=d"
    response = requests.get(download_url)
    print(response)
    if response.status_code == 200:
        file_path = os.path.join(download_folder, media_item["filename"])
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {media_item['filename']}")


def get_all_albums():
    """Retrieve all albums from the user's Google Photos account."""

    try:
        creds = get_credentials()
        service = build(
            "photoslibrary", "v1", credentials=creds, static_discovery=False
        )
        albums = []
        next_page_token = None
        while True:
            album_request = service.albums().list(
                pageSize=50, pageToken=next_page_token
            )
            album_response = album_request.execute()
            albums.extend(album_response.get("albums", []))
            next_page_token = album_response.get("nextPageToken")
            if next_page_token is None:
                break
        return albums
    except:
        return None


def download_album_items(album_id, download_folder):

    creds = get_credentials()
    service = build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    try:
        results = (
            service.mediaItems()
            .search(
                body={
                    "albumId": album_id,
                    "pageSize": 10,
                }
            )
            .execute()
        )
        items = results.get("mediaItems", [])

        print(items)
        for item in items:
            print(item)
            download_mediaitem(item, download_folder)

        return items
    except Exception as e:
        print(e)
        return False
