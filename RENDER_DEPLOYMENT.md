# 🚀 Render.com Deployment Guide

## Your Deployment Information

**Project**: LLM Code Deployment System  
**GitHub Username**: 21f3000813  
**Repository**: llm-deployment-api  

## Step-by-Step Deployment

### 1. Create GitHub Repository

1. Go to: **https://github.com/new**
2. Settings:
   - **Repository name**: `llm-deployment-api`
   - **Description**: `LLM Code Deployment System - Automated app generation and deployment`
   - **Visibility**: ✅ **Public**
   - **DO NOT** check "Add a README file"
   - **DO NOT** add .gitignore or license (we already have them)
3. Click **"Create repository"**

### 2. Push Code to GitHub

The code is ready! Just run these commands:

```powershell
cd "C:\Users\Asus\Desktop\TDS-1 Project"

# Add remote
git remote add origin https://github.com/21f3000813/llm-deployment-api.git

# Push to GitHub
git push -u origin main
```

If you get "branch main doesn't exist" error, run:
```powershell
git branch -M main
git push -u origin main
```

### 3. Deploy to Render

1. **Sign Up/Login to Render**
   - Go to: **https://render.com**
   - Click **"Get Started for Free"** or **"Sign In"**
   - Choose **"Continue with GitHub"**
   - Authorize Render to access your repositories

2. **Create New Web Service**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**
   - Find and select your repository: `21f3000813/llm-deployment-api`
   - Click **"Connect"**

3. **Configure Service**
   Fill in these settings:

   | Setting | Value |
   |---------|-------|
   | **Name** | `llm-deployment-api` |
   | **Region** | `Singapore` (or closest to you) |
   | **Branch** | `main` |
   | **Runtime** | `Node` |
   | **Build Command** | `npm install` |
   | **Start Command** | `npm start` |
   | **Instance Type** | `Free` |

4. **Add Environment Variables**
   
   Click **"Advanced"** → Scroll to **"Environment Variables"** → Click **"Add Environment Variable"**
   
   Add these **one by one**:

   ```
   Key: NODE_ENV
   Value: production
   ```

   ```
   Key: STUDENT_API_PORT
   Value: 3000
   ```

   ```
   Key: STUDENT_SECRET
   Value: MyUniqueSecret2025
   ```

   ```
   Key: STUDENT_EMAIL
   Value: 21f3000813@ds.study.iitm.ac.in
   ```

   ```
   Key: GITHUB_TOKEN
   Value: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   ```
   Key: GITHUB_USERNAME
   Value: 21f3000813
   ```

   ```
   Key: OPENAI_API_KEY
   Value: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   ```
   Key: LLM_PROVIDER
   Value: openai
   ```

   ```
   Key: MAX_RETRIES
   Value: 5
   ```

   ```
   Key: RETRY_DELAYS
   Value: 1,2,4,8,16
   ```

   ```
   Key: REQUEST_TIMEOUT_MINUTES
   Value: 10
   ```

5. **Deploy!**
   - Click **"Create Web Service"** at the bottom
   - Wait 2-3 minutes for deployment
   - Watch the logs for any errors

### 4. Get Your Live URL

After deployment completes, you'll see:
```
==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉

https://llm-deployment-api.onrender.com
```

Copy this URL!

### 5. Test Your Deployed API

```powershell
# Health check
curl https://llm-deployment-api.onrender.com/health

# Expected response:
# {"status":"ok","timestamp":"2025-10-17T..."}
```

### 6. Update sample_request.json for Testing

Update the evaluation_url in sample_request.json to use your deployed URL or keep it as localhost for testing.

### 7. Submit to Google Form

Your final answers:

```
✅ API URL: https://llm-deployment-api.onrender.com/api/submit

✅ Secret: MyUniqueSecret2025

✅ GitHub: https://github.com/21f3000813
```

## Important Notes

### ⚠️ Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds (cold start)
- 750 hours/month free tier

### 💡 Cold Start Handling
When the service is "asleep":
1. First request wakes it up (30-60 seconds)
2. You'll get HTTP 200 response
3. Subsequent requests are instant

### 🔒 Security
- Never commit your `.env` file
- Environment variables are encrypted on Render
- GitHub token is secure
- API key is protected

### 📊 Monitoring
- View logs: Render Dashboard → Your Service → Logs
- Check health: Visit `https://your-url.onrender.com/health`
- Monitor deploys: Render Dashboard → Your Service → Events

## Troubleshooting

### Build Failed
**Check logs for:**
- Missing dependencies in package.json
- Node.js version issues
- Build command errors

**Solution:** Check Render logs and fix errors

### Service Won't Start
**Common issues:**
- Wrong PORT configuration
- Missing environment variables
- Start command incorrect

**Solution:** Verify all environment variables are set

### GitHub Authentication Failed
**Issue:** Can't connect to GitHub

**Solution:**
1. Check GitHub token hasn't expired
2. Verify GITHUB_USERNAME is correct (no URL, just username)
3. Regenerate token if needed

### LLM API Errors
**Issue:** OpenAI API fails

**Solution:**
1. Check API key is valid
2. Verify you have credits
3. Check rate limits

## Next Steps After Deployment

1. ✅ Test health endpoint
2. ✅ Submit to Google Form
3. ✅ Wait for instructor's test request
4. ✅ Monitor Render logs during evaluation
5. ✅ Keep repository public
6. ✅ Don't delete the service until after grading

## Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **GitHub Issues**: Create issue in your repo

---

**Good luck with your deployment! 🚀**
