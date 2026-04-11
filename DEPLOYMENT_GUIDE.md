# AI Medical Diagnosis App - Deployment Guide

## Quick Deployment Options

### 1. Vercel (Recommended - Free & Easy)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd web
vercel --prod
```

### 2. Netlify (Free)
1. Go to https://netlify.com
2. Drag and drop the `web/build` folder
3. Your app will be live instantly!

### 3. GitHub Pages (Free)
1. Push code to your GitHub: https://github.com/shiva8439/major-project
2. Go to Settings > Pages
3. Select `main` branch and `/build` folder
4. Your app will be live at `https://shiva8439.github.io/major-project`

## Important Notes

### Backend Requirement
Your web app needs the backend API to work. For public deployment, you need to:

1. **Deploy Backend First** (choose one):
   - **Railway**: https://railway.app (Free tier available)
   - **Render**: https://render.com (Free tier available)
   - **Heroku**: https://heroku.com (Paid)
   - **DigitalOcean**: https://digitalocean.com (Paid)

2. **Update API URL** in web app:
   - Change `http://localhost:8000` to your deployed backend URL
   - File: `web/src/components/ImageUploadScreen.js`

### For Testing Without Backend
The frontend will work but show "API connection failed" - this is normal without backend.

## Files Ready for Deployment
- Frontend: `web/build/` folder (69.72 kB optimized)
- Backend: Needs separate deployment

## One-Click Deployment
```bash
# From project root
cd web
npm run deploy
# Upload the build folder to any hosting service
```

Your app is now ready for the world!
