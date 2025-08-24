# 🚀 Render Deployment Guide

## Quick Deploy on Render

### Step 1: Deploy
1. **Go to [render.com](https://render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure**:
   - **Name**: `medical-symptoms-agent`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: `Free`

### Step 2: Environment Variables (Optional)
Add in Render dashboard:
```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
```

### Step 3: Deploy
Click "Create Web Service"

## 🎉 Success
Your app will be live at: `https://your-app-name.onrender.com`
