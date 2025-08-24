# 🐳 Docker Deployment Guide

## 🚀 Deploy Using Docker (Recommended for Render)

Since Render's Python build is having issues, we're using Docker deployment instead.

### **Step 1: Render Docker Deployment**

1. **Go to [render.com](https://render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure**:
   - **Name**: `medical-symptoms-agent`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: `Free`

### **Step 2: Environment Variables**

In Render dashboard, add these environment variables:
```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
```

### **Step 3: Deploy**

Click "Create Web Service" and wait for deployment.

## 🎯 **Why Docker Works Better**

- ✅ **No Python version conflicts** - Uses Python 3.10 in container
- ✅ **No build wheel errors** - Docker handles dependencies
- ✅ **Consistent environment** - Same everywhere
- ✅ **No setup.py issues** - Clean container build

## 📋 **Files for Docker Deployment**

- `Dockerfile` - Container configuration
- `requirements-minimal.txt` - Minimal dependencies
- `render.yaml` - Docker deployment config

## 🆘 **If Docker Fails**

**Try Vercel instead** - Often more reliable:
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Deploy in 2-3 minutes

## 🎉 **Success**

Once deployed, your app will be live at:
`https://your-app-name.onrender.com`
