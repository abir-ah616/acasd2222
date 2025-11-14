# Deploying to Render.com (Free Tier)

## Important Limitations of Free Tier

⚠️ **Render's free tier has these limitations:**
- **Spins down after 15 minutes of inactivity** (your bot will disconnect from game)
- **Spins up when someone visits** (takes 30-60 seconds to start)
- **750 hours/month limit** (not truly 24/7)
- Not ideal for a bot that needs to stay connected to game servers

**Better option:** Replit's deployment keeps your bot running 24/7 without these issues.

---

## If You Still Want to Use Render

### Step 1: Prepare Your GitHub Repository

1. Create a new repository on GitHub
2. Push all your files to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name:** `freefire-bot-panel` (or any name you want)
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh`
   - **Plan:** `Free`

4. Add environment variable:
   - Key: `PORT`
   - Value: `5000`

5. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- Render will build and deploy your app
- First deployment takes 3-5 minutes
- You'll get a URL like: `https://your-app-name.onrender.com`

### Step 5: Access Your Bot

- Visit your Render URL
- The web panel should load
- **Remember:** On free tier, if no one visits for 15 minutes, the bot shuts down and disconnects from game

---

## Alternative: Use Render.yaml (Easier)

The `render.yaml` file is already created in your project. When deploying:

1. Connect your GitHub repo to Render
2. Render will automatically detect `render.yaml`
3. Just click "Apply" and it will deploy with the correct settings

---

## Troubleshooting

**Bot keeps disconnecting:**
- This is normal on free tier - it spins down after 15 minutes
- Upgrade to paid plan ($7/month) for 24/7 uptime
- Or use Replit deployment instead

**Build fails:**
- Check that `requirements.txt` is in your repo
- Make sure `start.sh` is executable
- Check Render logs for specific errors

**Port issues:**
- Make sure web_panel.py uses `os.environ.get('PORT', 5000)`
- Already configured in your current setup

---

## Cost Comparison

| Platform | Free Tier | Always Running | Best For |
|----------|-----------|----------------|----------|
| Render | ✅ Yes | ❌ No (spins down) | Testing |
| Replit | ✅ Yes | ✅ Yes (on paid) | 24/7 bots |
| Railway | ✅ $5 credit | ✅ Yes | Small apps |

**Recommendation:** For a Free Fire bot that needs to stay connected, Replit deployment is your best free option for reliable uptime.
