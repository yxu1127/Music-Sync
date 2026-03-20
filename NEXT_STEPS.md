# Next Steps: Deploy to Render

You've set up Supabase. Here's what to do next.

---

## Step 1: Push Your Code to GitHub

1. Open Terminal and go to your project folder:
   ```bash
   cd "/Users/evie/Documents/Cursor/Music downloader"
   ```

2. Check if you have uncommitted changes:
   ```bash
   git status
   ```

3. If there are changes, add and push:
   ```bash
   git add .
   git commit -m "Add Supabase support"
   git push
   ```

---

## Step 2: Create a Web Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in.

2. Click **New +** (top right) → **Web Service**.

3. Connect GitHub if needed:
   - Click **Connect account** next to GitHub.
   - Authorize Render to access your repos.

4. Find your repository (e.g. `Music-Sync`) and click **Connect**.

---

## Step 3: Configure the Service

1. **Name:** `music-downloader` (or any name you like).

2. **Region:** Choose the one closest to you.

3. **Branch:** `main`.

4. **Runtime:** Select **Docker**.

5. **Plan:** Select **Free**.

---

## Step 4: Add Environment Variables

Click **Advanced** to expand options, then click **Add Environment Variable**.

Add these one by one:

| Key | Value | Secret? |
|-----|-------|---------|
| `COOKIES_BASE64` | *(paste from your cookies_base64.txt)* | ✓ Yes |
| `PYTHONUNBUFFERED` | `1` | No |
| `SUPABASE_URL` | *(your Supabase Project URL, e.g. https://xxx.supabase.co)* | No |
| `SUPABASE_KEY` | *(your Supabase Secret key)* | ✓ Yes |

**If you use Google Drive**, also add:

| Key | Value | Secret? |
|-----|-------|---------|
| `GOOGLE_CREDENTIALS_JSON` | *(paste from creds_b64.txt)* | ✓ Yes |
| `GOOGLE_TOKEN_JSON` | *(paste from token_b64.txt)* | ✓ Yes |

---

## Step 5: Deploy

1. Click **Create Web Service**.

2. Render will start building. This takes about 5–10 minutes.

3. Watch the **Logs** tab. When you see something like "Uvicorn running on...", the build is done.

4. Copy your service URL (e.g. `https://music-downloader-xxxx.onrender.com`).

---

## Step 6: Use Your App

1. Open the URL in your browser.

2. Add a playlist by pasting a YouTube Music playlist URL and clicking **Add**.

3. Click **Sync now** to download tracks.

4. Playlists you add here are saved in Supabase and will persist across redeploys.

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| **"Failed to fetch playlists"** | Wait 30–60 seconds (service may be waking up). Check Render Logs for errors. |
| **403 / Download fails** | Update `COOKIES_BASE64` — export fresh cookies from YouTube Music. |
| **Blank page** | Wait for the build to finish. Check that `frontend/dist` exists in your repo. |
| **Supabase connection error** | Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct. No extra spaces. |
