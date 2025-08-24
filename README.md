# Medical Symptoms-to-Diagnosis Agent

A Flask-based web application that analyzes medical symptoms and provides potential diagnoses using AI.

## 🐳 Deploy with Docker

### Quick Docker Deployment:

1. **Build the Docker image:**
   ```bash
   docker build -t medical-symptoms-agent .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 medical-symptoms-agent
   ```

3. **Access your app at:** `http://localhost:5000`

### Deploy to Cloud Platforms:

#### **Railway (Recommended)**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Docker and deploy

#### **Fly.io**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Deploy: `fly launch`
4. Follow prompts

#### **Google Cloud Run**
1. Build and push to Google Container Registry
2. Deploy to Cloud Run
3. Get your live URL

### Environment Variables (Optional):
```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
```

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
