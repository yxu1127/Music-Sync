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

### 2a. Install a cookie export extension

**Chrome:**
1. Open [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Click **Add to Chrome** → **Add extension**

**Firefox:**
1. Open [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Click **Add to Firefox** → **Add**

### 2b. Sign in and export cookies

1. Go to [music.youtube.com](https://music.youtube.com) in the same browser.
2. Sign in to your Google account if you aren’t already.
3. Make sure you can see your playlists (you’re fully logged in).
4. Click the extension icon in your toolbar (puzzle piece → “Get cookies.txt LOCALLY” or “cookies.txt”).
5. In the extension:
   - **Chrome:** Click **Export** or **Get cookies**. It will download a file.
   - **Firefox:** Select **Current site** or enter `youtube.com`, then export.
6. Save the file as `cookies.txt` in your project folder (or wherever you prefer).
7. The file should be in Netscape format: it starts with `# Netscape HTTP Cookie File` and has lines like `youtube.com	TRUE	/	...`.

### 2c. Encode for Render (run in Terminal)

   **macOS/Linux:**
   ```bash
   base64 -i cookies.txt | tr -d '\n' > cookies_base64.txt
   ```

   **Windows (PowerShell):**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt")) | Set-Content cookies_base64.txt -NoNewline
   ```

### 2d. Copy the encoded value

Open `cookies_base64.txt` and copy its entire contents. You’ll paste this into Render as the `COOKIES_BASE64` secret in Step 5.

**Tip:** If your extension lets you choose the domain, pick `youtube.com` so you get cookies for both youtube.com and music.youtube.com.

---

## Step 3: Set Up Google Drive (Where Downloads Go)

Render's disk is temporary. Use Google Drive so your downloaded tracks persist.

### 3a. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and sign in.
2. Click the project dropdown at the top (next to "Google Cloud").
3. Click **New Project**.
4. Enter a name (e.g. "Music Sync") and click **Create**.
5. Wait for the project to be created, then select it from the dropdown.

### 3b. Enable Google Drive API

1. In the left sidebar, go to **APIs & Services** → **Library** (or search "API Library").
2. Search for **Google Drive API**.
3. Click **Google Drive API** → **Enable**.

### 3c. Create OAuth credentials

1. Go to **APIs & Services** → **Credentials**.
2. Click **+ Create Credentials** → **OAuth client ID**.
3. If prompted to configure the OAuth consent screen:
   - Choose **External** (unless you have a Google Workspace org) → **Create**.
   - Fill in **App name** (e.g. "Music Sync") and **User support email** (your email).
   - Click **Save and Continue** through the scopes (default is fine).
   - Add your email under **Test users** if needed → **Save and Continue**.
4. Back at **Create OAuth client ID**:
   - **Application type:** **Desktop app**.
   - **Name:** e.g. "Music Sync Desktop".
   - Click **Create**.
5. Click **Download** (JSON) next to your new client.
6. Rename the downloaded file to `credentials.json` and move it into your project folder (same folder as `config.yaml`).

### 3d. Run OAuth locally (one-time authorization)

1. Open Terminal and go to your project folder:
   ```bash
   cd "/Users/evie/Documents/Cursor/Music downloader"
   ```

2. Run the app (or just the Drive auth):
   ```bash
   python -c "from src.drive_uploader import get_drive_service; get_drive_service()"
   ```

3. A browser window will open. Sign in to the Google account where you want the music saved.

4. Click **Allow** when asked for permission to access Google Drive.

5. The script will finish and create `token_drive.json` in your project folder. You can close the browser.

### 3e. Encode both files for Render

Run in Terminal from your project folder:

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

Open `creds_b64.txt` and `token_b64.txt`, copy each file's contents. You'll paste them into Render as secrets in Step 5.

### 3f. Update config.yaml

1. Open `config.yaml` in your project folder.

2. Set the storage section:
   ```yaml
   storage:
     local: false
     google_drive: true
     drive_folder_id: ''   # Leave empty to create "YouTube Music" at root
   ```

3. Comment out `cookies_browser` in the download section (you'll use cookies file instead):
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

**Or use Supabase (Step 4b)** so playlists added via the website persist across redeploys.

---

## Step 4b (Optional): Use Supabase for Persistent Playlists

With Supabase, playlists you add via the Render website are saved in a database and survive redeploys.

### 4b.1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in (or create an account).
2. On the dashboard, click **New Project**.
3. Fill in:
   - **Organization:** Select or create one.
   - **Name:** e.g. `music-sync`.
   - **Database Password:** Create a strong password and save it.
4. Click **Create new project**.
5. Wait 1–2 minutes for the project to finish setting up.

### 4b.2. Create the playlists table

1. In the left sidebar, click **SQL Editor** (icon looks like `</>` or a code bracket).
2. Click the **+ New query** button (top right of the SQL Editor area).
3. A blank editor will open. Delete any placeholder text.
4. Copy and paste this SQL into the editor:

   ```sql
   create table if not exists playlists (
     id text primary key,
     name text not null default 'Unknown Playlist',
     paused boolean not null default false,
     thumbnail text
   );
   ```

5. Click the **Run** button (or press Ctrl+Enter / Cmd+Enter).
6. You should see "Success. No rows returned" — that means the table was created.

### 4b.3. Get your API keys

1. In the left sidebar, click the **gear icon** (⚙️) at the bottom to open **Project Settings**.
2. In the settings menu, click **API**.
3. On the API page:
   - Under **Project URL**, click the copy icon to copy the URL (e.g. `https://abcdefgh.supabase.co`).
   - Under **Project API keys**, find **service_role** (not anon). Click **Reveal** if needed, then copy it.
4. Save both somewhere safe — you'll add them to Render in Step 5.

### 4b.4. Add env vars in Render (Step 5)

When you deploy on Render, add these environment variables:

| Key | Value | Secret? |
|-----|-------|---------|
| `SUPABASE_URL` | *(paste your Project URL)* | No |
| `SUPABASE_KEY` | *(paste your service_role key)* | Yes |

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

7. If you use Supabase (Step 4b), add:
   | Key            | Value                    | Secret? |
   |----------------|--------------------------|---------|
   | `SUPABASE_URL` | *(your Project URL)*     | No      |
   | `SUPABASE_KEY` | *(your service_role key)*| Yes     |

8. Click **Create Web Service**.

8. Wait for the build to finish (about 5–10 minutes).

9. When it’s live, open the URL (e.g. `https://music-downloader-xxxx.onrender.com`).

---

## Step 6: Done

Open your Render URL and start syncing.

---

## Limitations (Free Tier)

| Limitation | Impact |
|------------|--------|
| **Ephemeral disk** | Config changes and `state.db` reset on redeploy or cold start. Use Supabase (Step 4b) so playlists persist. |
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
