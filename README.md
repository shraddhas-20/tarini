# 🌸 TARINI - Women Safety Companion

**Always By Her Side** - A comprehensive women safety web application with emergency features, voice notes, and support network management.

## 🚀 Features

- **Emergency SOS System** - Quick access to emergency services
- **Fake Call Feature** - Escape uncomfortable situations with realistic fake calls
- **Voice Notes** - Pre-record and manage emergency voice messages
- **Emergency Contacts** - Manage trusted contacts for quick access
- **Safety Dashboard** - Centralized hub for all safety features
- **User Authentication** - Secure registration and login system
- **Responsive Design** - Beautiful pink/white theme with mobile support

## 🎨 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with glass morphism effects
- **Authentication**: bcrypt password hashing
- **File Handling**: Audio file uploads for voice notes

## 🚂 Railway Deployment

This application is configured for easy deployment on Railway.

### Quick Deploy

1. **Fork this repository** to your GitHub account

2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked `tarini` repository

3. **Set Environment Variables** (in Railway dashboard):
   ```
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=production
   ```

4. **Deploy**: Railway will automatically build and deploy your application!

### Manual Railway Setup

If you prefer manual setup:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variables set SECRET_KEY=your-super-secret-key-here
railway variables set FLASK_ENV=production

# Deploy
railway up
```

## 🏃‍♀️ Local Development

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shraddhas-20/tarini.git
   cd tarini
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the app**: Open http://localhost:5001 in your browser

## 📁 Project Structure

```
tarini/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway/Heroku deployment config
├── runtime.txt           # Python version specification
├── railway.json          # Railway-specific configuration
├── start.sh              # Application startup script
├── tarini_safety.db      # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── index.html        # Homepage
│   ├── dashboard.html    # User dashboard
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── about.html        # About page
│   ├── manage_contacts_simple.html  # Emergency contacts
│   └── voice_notes.html  # Voice notes management
├── statics/              # Static assets
│   └── contacts.png      # Contact icon
└── uploads/              # File uploads
    └── voice_notes/      # Voice note files
```

## 🎯 Usage Guide

### Getting Started
1. **Register** - Create your safety profile with emergency contact
2. **Dashboard** - Access all safety features from the main dashboard
3. **Emergency Contacts** - Add trusted contacts for quick access
4. **Voice Notes** - Upload pre-recorded messages for fake calls

### Emergency Features
- **SOS Button** - Instantly contact emergency services
- **Fake Call** - Simulate incoming calls to escape situations
- **Emergency Contacts** - Quick access to trusted contacts
- **Voice Messages** - Use pre-recorded audio for realistic fake calls

## 🔒 Security Features

- **Password Hashing** - bcrypt encryption for user passwords
- **Session Management** - Secure user sessions
- **Input Validation** - Protection against common web vulnerabilities
- **File Upload Security** - Restricted file types for voice notes

## 🌈 UI/UX Features

- **Mixed Theme** - Beautiful pink headers with white backgrounds
- **Glass Morphism** - Modern translucent design elements
- **Responsive Design** - Works perfectly on mobile and desktop
- **Animated Elements** - Smooth transitions and hover effects
- **Consistent Headers** - Standardized 80px headers across all pages

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💝 Acknowledgments

- Built with love for women's safety
- Inspired by the need for accessible safety technology
- Dedicated to empowering women through technology

---

**TARINI** - Because every woman deserves to feel safe, always. 🌸✨