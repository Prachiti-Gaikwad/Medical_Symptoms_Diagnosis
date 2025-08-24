# Medical Symptoms-to-Diagnosis Agent

A Flask-based web application that analyzes medical symptoms and provides potential diagnoses using AI.

## 🚀 Deploy on Render

### Quick Deployment Steps:

1. **Fork/Clone this repository**
2. **Go to [render.com](https://render.com)**
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure**:
   - **Name**: `medical-symptoms-agent`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: `Free`

### Environment Variables (Optional):

Add these in Render dashboard:
```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
```

### Your app will be live at:
`https://your-app-name.onrender.com`

## 🏃‍♂️ Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## 📋 Features

- Symptom analysis and diagnosis
- Medical image recognition
- Multi-language support
- Health check endpoint
- Educational medical information

## ⚠️ Disclaimer

This application is for educational purposes only. Always consult healthcare professionals for medical advice. 
