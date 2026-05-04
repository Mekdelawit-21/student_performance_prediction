# Deployment Guide

## Project Structure

This project consists of:
- **Backend**: Flask application with ML models for student performance prediction
- **Frontend**: HTML templates with JavaScript for user interface

## Deployment Options

### Option 1: Deploy Entire App to Render (Recommended)

Since this is a Flask app with server-side rendered templates, the simplest deployment is to deploy the entire application to Render.

#### Steps:

1. **Push to GitHub** (already done)
   - Repository: https://github.com/Mekdelawit-21/student_performance_prediction

2. **Deploy to Render**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `student_performance_project-master/student_performance_project-master/student_performance_app` folder
   - Use the following settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Python Version**: 3.12.0
   - Click "Deploy Web Service"

3. **Environment Variables** (if needed)
   - PORT: Render automatically sets this
   - No additional environment variables needed for this app

### Option 2: Separate Frontend (Vercel) and Backend (Render)

If you want to deploy the frontend separately on Vercel:

#### Backend Deployment (Render)

1. Deploy the Flask app to Render as described in Option 1
2. Note the Render backend URL (e.g., `https://student-performance-backend.onrender.com`)

#### Frontend Deployment (Vercel)

1. Create a new folder for the frontend
2. Copy the `templates` folder content to a static HTML/JS structure
3. Update the JavaScript to call the Render backend API instead of relative URLs
4. Deploy to Vercel:
   - Go to https://vercel.com
   - Click "New Project"
   - Import from GitHub
   - Deploy

## Current Deployment Files

- `render.yaml`: Render configuration for backend deployment
- `requirements.txt`: Python dependencies for Render
- `vercel.json`: Vercel configuration (for Option 2)

## Quick Start

1. **For Render deployment** (recommended):
   - Just deploy the `student_performance_app` folder to Render
   - Render will automatically detect the Python app and deploy it

2. **For Vercel + Render**:
   - First deploy backend to Render
   - Then create a separate frontend repo for Vercel
   - Update frontend API calls to use the Render backend URL

## Notes

- The Flask app is configured to use the PORT environment variable (required by Render)
- Models are trained on startup if not found in the `models/` directory
- The app uses `gunicorn` as the production WSGI server
