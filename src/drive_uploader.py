"""Upload files to Google Drive."""

import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# drive.file = minimal; drive = can create folders at root
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_credentials_path() -> Path:
    """Return path to credentials or token file."""
    project_root = Path(__file__).parent.parent
    return project_root


def get_drive_service(credentials_path: Optional[str] = None) -> object:
    """
    Authenticate and return Google Drive API service.
    Uses credentials.json for first-time auth, token_drive.json thereafter.
    """
    project_root = Path(__file__).parent.parent
    creds_file = Path(credentials_path) if credentials_path else project_root / "credentials.json"
    token_file = project_root / "token_drive.json"

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_file.exists():
                raise FileNotFoundError(
                    f"credentials.json not found. Create OAuth credentials at "
                    "console.cloud.google.com, enable Drive API, download as credentials.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_file(
    service: object,
    file_path: str,
    folder_id: Optional[str] = None,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """
    Upload a file to Google Drive.
    Returns the file ID, or None on failure.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return None

    name = file_name or file_path.name
    mime_type = "audio/wav" if file_path.suffix.lower() == ".wav" else "application/octet-stream"

    file_metadata = {"name": name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    # Use resumable upload for large files (WAV can be 50MB+)
    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

    try:
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file.get("id")
    except Exception as e:
        print(f"Drive upload failed: {e}")
        return None


def ensure_folder(service: object, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
    """
    Create folder if it doesn't exist, or find existing one.
    Returns folder ID. parent_id=None means create at root.
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"

    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    # Create folder
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]

    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")
