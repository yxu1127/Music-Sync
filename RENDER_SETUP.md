# Render Deployment Guide (Personal Use)

Deploy the app to Render so you can **open a URL in your browser and use it** — no terminal, no local server.

**After setup:** Just go to your Render URL (e.g. `https://music-downloader-xxxx.onrender.com`) and use the app like any website.

---

## Prerequisites

- A [GitHub](https://github.com) account
- A [Render](https://render.com) account (free)
- [Google Drive](https://drive.google.com) (for storing downloads — Render's disk is temporary)
- Your YouTube playlists added to `config.yaml` before deploying

---

## Step 1: Push Your Code to GitHub

1. Create a new repository on GitHub (e.g. `music-downloader`).
2. In your project folder, run:

```bash
cd "Music downloader"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/music-downloader.git
git push -u origin main
```

---

## Step 2: Export YouTube Cookies

Render has no browser, so you must provide cookies for YouTube access.

1. Install a browser extension that exports cookies in Netscape format:
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. Go to [music.youtube.com](https://music.youtube.com) and sign in.

3. Use the extension to export cookies for `youtube.com` → save as `cookies.txt`.

4. Encode the file for Render (run in Terminal):

   **macOS/Linux:**
   ```bash
   base64 -i cookies.txt | tr -d '\n' > cookies_base64.txt
   ```

   **Windows (PowerShell):**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt")) | Set-Content cookies_base64.txt -NoNewline
   ```

5. Open `cookies_base64.txt` and copy its contents — you'll paste this into Render in Step 5.

---

## Step 3: Set Up Google Drive (for Storing Downloads)

Render's disk is temporary. Use Google Drive so downloads persist.

1. In [Google Cloud Console](https://console.cloud.google.com/):
   - Create a project (or use an existing one)
   - Enable **Google Drive API**
   - Create **OAuth 2.0 Client ID** (Desktop app)
   - Download credentials → save as `credentials.json` in your project folder

2. **Run OAuth locally once** (so you get a refresh token):
   - Start the app locally: `./run.sh` or `python api.py`
   - Add a playlist and trigger a sync, or run: `python -c "from src.drive_uploader import get_drive_service; get_drive_service()"`
   - A browser will open — sign in to Google and authorize
   - This creates `token_drive.json` in your project folder

3. Encode both files for Render (run in Terminal from project folder):

   **macOS/Linux:**
   ```bash
   base64 -i credentials.json | tr -d '\n' > creds_b64.txt
   base64 -i token_drive.json | tr -d '\n' > token_b64.txt
   ```

   **Windows (PowerShell):**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json")) | Set-Content creds_b64.txt -NoNewline
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("token_drive.json")) | Set-Content token_b64.txt -NoNewline
   ```

   Copy the contents of each file — you'll add them as Render secrets in Step 5.

4. In `config.yaml`, set:

```yaml
storage:
  local: false
  google_drive: true
  drive_folder_id: ''   # Leave empty to create "YouTube Music" at root
```

5. Remove or comment out `cookies_browser` in the download section (you'll use cookies file instead):

```yaml
download:
  output_dir: ./downloads
  format: wav
  quality: '0'
  # cookies_browser: chrome   # Not used on Render
```

---

## Step 4: Add Playlists to config.yaml

Before deploying, add your playlists to `config.yaml` so they persist across deploys:

```yaml
playlists:
  - id: PLxxxxxxxxxxxxxxxxxx
    name: My Favorites
    paused: false
  # Add more playlists...
```

You can add more later via the web UI, but they will be lost when the service restarts or redeploys. For reliability, keep your main playlists in `config.yaml` in the repo.

---

## Step 5: Deploy on Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in.

2. Click **New +** → **Web Service**.

3. Connect your GitHub account if needed, then select your `music-downloader` repository.

4. Configure the service:
   - **Name:** `music-downloader` (or any name)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Runtime:** **Docker**
   - **Plan:** **Free**

5. Add environment variables (click **Advanced** → **Add Environment Variable**):

   | Key            | Value                    | Secret? |
   |----------------|--------------------------|---------|
   | `COOKIES_BASE64` | *(paste from cookies_base64.txt)* | Yes     |
   | `PYTHONUNBUFFERED` | `1`                  | No      |

6. If you use Google Drive, add two more secrets:
   | Key            | Value                    | Secret? |
   |----------------|--------------------------|---------|
   | `GOOGLE_CREDENTIALS_JSON` | *(paste from creds_b64.txt)* | Yes     |
   | `GOOGLE_TOKEN_JSON` | *(paste from token_b64.txt)* | Yes     |

7. Click **Create Web Service**.

8. Wait for the build to finish (about 5–10 minutes).

9. When it’s live, open the URL (e.g. `https://music-downloader-xxxx.onrender.com`).

---

## Step 6: Done

Open your Render URL and start syncing.

---

## Limitations (Free Tier)

| Limitation | Impact |
|------------|--------|
| **Ephemeral disk** | Config changes and `state.db` reset on redeploy or cold start. Keep playlists in `config.yaml` in the repo. |
| **Spin-down** | Service sleeps after ~15 min of inactivity. First visit may take 30–60 seconds to wake. |
| **No browser** | Must use `COOKIES_BASE64`; `cookies_browser` does not work. |
| **Storage** | Use Google Drive for downloads; local disk is temporary. |

---

## Updating Your Deployment

After changing code or config:

```bash
git add .
git commit -m "Update"
git push
```

Render will automatically redeploy. Remember: any playlists or settings added only via the web UI will be lost on redeploy. Keep important playlists in `config.yaml` in the repo.

---

## Troubleshooting

- **403 / Download fails:** Refresh your cookies. Export again from YouTube Music and update `COOKIES_BASE64`.
- **Build fails:** Ensure `frontend/` and `requirements.txt` are in the repo and the Dockerfile is at the project root.
- **Blank page:** Wait for the build to finish. Check the Logs tab for errors.
- **Google Drive auth:** Re-run the OAuth flow if `token_drive.json` was lost after a restart.
