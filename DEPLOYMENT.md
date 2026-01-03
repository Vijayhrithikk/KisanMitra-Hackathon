# 🚀 KisanMitra Deployment Guide

## Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

## Step 2: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repo
4. Add Environment Variables:
   - `VITE_ML_API_URL` = (will add after Step 3)
   - `VITE_MARKET_API_URL` = (will add after Step 4)
5. Click **Deploy**

---

## Step 3: Deploy ML Engine (Render)

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Settings:
   - **Name**: `kisanmitra-ml-engine`
   - **Root Directory**: `backend/ml_engine`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Click **Deploy**
6. Copy the URL (e.g., `https://kisanmitra-ml-engine.onrender.com`)

---

## Step 4: Deploy Marketplace API (Render)

1. Click **"New +"** → **"Web Service"**
2. Connect same GitHub repo
3. Settings:
   - **Name**: `kisanmitra-marketplace`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn marketplace_api:app --bind 0.0.0.0:$PORT`
4. Add Environment Variable:
   - `MONGO_URI` = (your MongoDB Atlas connection string)
5. Click **Deploy**
6. Copy the URL (e.g., `https://kisanmitra-marketplace.onrender.com`)

---

## Step 5: Update Vercel Environment Variables

Go back to Vercel → Project Settings → Environment Variables:

```
VITE_ML_API_URL = https://kisanmitra-ml.onrender.com
VITE_MARKET_API_URL = https://kisanmitra-api-fe31.onrender.com/api
```

- **ML Engine**: `https://kisanmitra-ml.onrender.com`
- **Marketplace API**: `https://kisanmitra-api-fe31.onrender.com/api`

Then click **Redeploy**.

---

## Step 6: MongoDB Atlas Setup

1. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a cluster (free tier)
3. Create database user
4. Get connection string
5. Add to Render environment variables

---

## ✅ Done!

Your app is now live at:
- **Frontend**: `https://your-app.vercel.app`
- **ML API**: `https://kisanmitra-ml-engine.onrender.com`
- **Market API**: `https://kisanmitra-marketplace.onrender.com`
