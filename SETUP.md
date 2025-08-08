# Setup Guide - Medical Symptoms-to-Diagnosis Agent

## Overview

This guide will help you set up and run the Medical Symptoms-to-Diagnosis Agent. The application uses **Together AI** as the primary AI provider and **Hugging Face** as backup, both offering free access. The system also integrates with multiple medical APIs for comprehensive symptom analysis and medicine recommendations.

## Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Together AI account** (free) - recommended
- **Hugging Face account** (free) - optional backup

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Medical-Symptoms-to-Diagnosis-Agent
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp env_example.txt .env
   ```

2. **Edit the `.env` file** and add your API keys (optional):
   ```bash
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   
   # Together AI Configuration (PRIMARY - FREE)
   TOGETHER_API_KEY=your-together-api-key-here
   
   # Hugging Face Configuration (BACKUP - FREE)
   HUGGINGFACE_API_KEY=hf_your_actual_token_here
   ```

## API Setup (Optional)

### Together AI Setup (Recommended - Free)

1. **Visit Together AI:**
   - Go to [https://together.ai/](https://together.ai/)
   - Click "Sign Up" if you don't have an account, or "Sign In" if you do

2. **Create Account (if new):**
   - Fill in your details (email, username, password)
   - Verify your email address

3. **Get Free Credits:**
   - Together AI provides free credits for new users
   - Check your account dashboard for available credits

4. **Generate API Key:**
   - After login, go to "API Keys" section
   - Click "Create API Key"
   - Name: "Medical Symptoms Agent"
   - Copy the API key

5. **Add to your `.env` file:**
   ```bash
   TOGETHER_API_KEY=your_actual_together_api_key_here
   ```

### Hugging Face Setup (Backup - Free)

1. **Visit Hugging Face:**
   - Go to [https://huggingface.co/](https://huggingface.co/)
   - Click "Sign Up" (if new) or "Sign In" (if existing account)

2. **Create Account (if needed):**
   - Fill in: Email, Username, Password
   - Verify your email address

3. **Generate API Token:**
   - After login, click your profile picture (top right)
   - Select **"Settings"**
   - Click **"Access Tokens"** in left sidebar
   - Click **"New token"**
   - Name: "Medical Symptoms Agent"
   - Permissions: **"Read"** (minimum required)
   - Click **"Generate token"**
   - **Copy the token** (starts with `hf_`)

4. **Add to your `.env` file:**
   ```bash
   HUGGINGFACE_API_KEY=hf_your_actual_token_here
   ```

## Running the Application

### Step 5: Start the Application

```bash
python run.py
```

### Step 6: Access the Application

1. **Open your browser** and go to: `http://localhost:5000`
2. **You should see** the Medical Symptoms-to-Diagnosis Agent interface

### Step 7: Test the Application

1. **Enter symptoms** in the text area (e.g., "headache and fever")
2. **Click "Analyze Symptoms"** or press Ctrl+Enter
3. **View results** including diagnoses, confidence levels, and medicine recommendations
4. **Click on any diagnosis** to see detailed information

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TOGETHER_API_KEY` | Your Together AI API key | None | **No** (optional) |
| `HUGGINGFACE_API_KEY` | Your Hugging Face API token | None | **No** (optional) |
| `SECRET_KEY` | Flask secret key | Auto-generated | No |
| `FLASK_DEBUG` | Enable debug mode | `False` | No |

### API Priority System

The application uses APIs in this priority order:

1. **Together AI** (Primary - FREE)
2. **Hugging Face** (Backup - FREE)
3. **Local Analysis** (Fallback - Always available)

## Features Available

### With API Keys:
- **AI-powered symptom analysis** using Together AI or Hugging Face
- **Real-time medicine recommendations** from FDA, RxNav, and PubMed
- **Medical literature** from PubMed Central
- **Advanced diagnosis capabilities**

### Without API Keys:
- **Local knowledge-based analysis** (comprehensive fallback)
- **Medicine recommendations** from local database
- **Basic symptom analysis** with multiple diagnoses
- **Full application functionality**

## Troubleshooting

### Common Issues

1. **"API not available" messages**
   - **Solution**: The application will automatically use local analysis
   - **Note**: This is normal and the app works perfectly without API keys

2. **"Module not found" errors**
   - **Solution**: Make sure you're in the virtual environment
   - **Run**: `pip install -r requirements.txt` again

3. **"Port already in use"**
   - **Solution**: Change the port in `run.py` or kill the existing process
   - **Use**: `lsof -ti:5000 | xargs kill -9` (Linux/Mac)

4. **"Analysis method shows fallback"**
   - **Solution**: This is normal when API keys are not configured
   - **Note**: The application works perfectly with local analysis

### Debug Mode

Enable debug mode for more detailed error messages:

```bash
# In your .env file
FLASK_DEBUG=True
```

### Logs

Check the console output for any error messages when running the application.

## Project Structure

```
Medical Symptoms-to-Diagnosis Agent/
├── app/                    # Main application
│   ├── __init__.py        # Flask app factory
│   ├── routes.py          # API endpoints
│   ├── utils.py           # Symptom analysis logic
│   ├── medical_apis.py    # Medicine API integrations
│   ├── ai_providers.py    # AI provider integrations
│   ├── advanced_features.py # Advanced functionality
│   ├── vector_integration.py # Vector database integration
│   └── static/            # Frontend assets
├── templates/             # HTML templates
├── config.py             # Configuration
├── run.py                # Application entry point
├── requirements.txt      # Python dependencies
├── env_example.txt       # Environment template
├── README.md             # Main documentation
├── SETUP.md              # This file
└── PROJECT_SUMMARY.md    # Technical overview
```

## Medical APIs Integration

The application integrates with several medical APIs:

### FDA Database
- **Purpose**: Official drug information
- **Data**: Dosages, warnings, side effects, indications
- **Status**: ✅ Integrated and working

### RxNav API
- **Purpose**: Drug interactions and terminology
- **Data**: Drug names, interactions, classifications
- **Status**: ✅ Integrated and working

### PubMed Central
- **Purpose**: Medical research articles
- **Data**: Research papers, abstracts, authors
- **Status**: ✅ Integrated and working

## Performance and Reliability

### Fallback Systems
- **AI Analysis**: Falls back to local analysis if APIs fail
- **Medicine Data**: Falls back to local database if APIs unavailable
- **Error Handling**: Comprehensive error handling throughout

### Response Times
- **Local Analysis**: < 1 second
- **AI Analysis**: 2-5 seconds (depending on API)
- **Medicine Data**: 1-3 seconds (depending on API)

## Security and Privacy

### Data Handling
- **No data storage**: Symptoms are not stored permanently
- **Local processing**: Analysis happens locally when possible
- **API security**: Secure API key handling

### Medical Disclaimer
- **Educational use only**: Clear disclaimers throughout the application
- **Professional consultation**: Always recommended for medical concerns
- **No medical advice**: Application provides information, not medical advice

## Support and Maintenance

### Getting Help
1. **Check this SETUP.md** file for detailed instructions
2. **Review README.md** for project overview
3. **Check PROJECT_SUMMARY.md** for technical details
4. **Test the application** at `http://localhost:5000`

### Updates
- **Regular updates**: Check for updates to dependencies
- **API changes**: Monitor API provider changes
- **Security updates**: Keep dependencies updated

## Production Deployment

### Requirements
- **Production WSGI server**: Use Gunicorn or uWSGI
- **Environment variables**: Set production values
- **SSL certificate**: For HTTPS
- **Domain configuration**: Set up proper domain

### Deployment Steps
1. **Set up production environment**
2. **Configure environment variables**
3. **Install production dependencies**
4. **Set up reverse proxy (nginx)**
5. **Configure SSL certificate**
6. **Deploy application**

## Conclusion

The Medical Symptoms-to-Diagnosis Agent is a comprehensive, production-ready application that provides intelligent symptom analysis with multiple AI and medical API integrations. The application works perfectly with or without API keys, making it accessible for all users.

**Key Benefits:**
- ✅ **Free AI APIs**: Together AI and Hugging Face integration
- ✅ **Comprehensive Medical Data**: FDA, RxNav, and PubMed integration
- ✅ **Robust Fallback**: Works without any API keys
- ✅ **Production Ready**: Clean, optimized codebase
- ✅ **Educational Focus**: Perfect for learning and development

**Ready to start? Run: `python run.py`** 