# Dishambha Awasthi - Portfolio Website

A modern, responsive portfolio website with a FastAPI backend and Django ORM database integration. Features contact form with WhatsApp and email notifications.

## 🚀 Features

- **Responsive Design** - Mobile-first, works on all devices
- **FastAPI Backend** - High-performance Python API
- **Django ORM** - SQLite database for contact messages
- **Notifications** - WhatsApp (Twilio) and Email (SMTP) alerts
- **Admin Panel** - View all contact submissions
- **API Documentation** - Interactive Swagger UI at `/api/docs`

## 📁 Project Structure

```
portfolio_backend/
├── main.py              # FastAPI application & routes
├── django_setup.py      # Django ORM configuration
├── models.py            # ContactMessage database model
├── migrate.py           # Database initialization
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── portfolio.db         # SQLite database
└── static/
    └── index.html       # Portfolio website
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/portfolio.git
cd portfolio
```

2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file
```bash
# Copy the template
cp portfolio_backend/.env.example portfolio_backend/.env
```

5. Edit `.env` with your credentials:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

TWILIO_SID=your-twilio-sid
TWILIO_TOKEN=your-twilio-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
MY_WHATSAPP=whatsapp:+919369879498

ADMIN_SECRET=your-secure-secret-key
```

6. Setup database
```bash
cd portfolio_backend
python migrate.py
```

7. Run the server
```bash
cd portfolio_backend
python main.py
```

Server will be available at: **http://localhost:8000**

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve portfolio HTML |
| POST | `/api/contact` | Submit contact form |
| GET | `/api/portfolio` | Get portfolio information |
| GET | `/api/messages?secret=YOUR_SECRET` | Admin: View all messages |
| GET | `/health` | Health check |
| GET | `/api/docs` | Swagger API documentation |

## 🔐 Environment Variables

Create a `.env` file in `portfolio_backend/` with:

```env
# Gmail SMTP (for email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-char-app-password

# Twilio (for WhatsApp notifications)
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TOKEN=your-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
MY_WHATSAPP=whatsapp:+919369879498

# Admin access
ADMIN_SECRET=your-random-secret-key
```

### Getting Credentials

**Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate and copy the 16-character password

**Twilio SID & Token:**
1. Go to https://www.twilio.com/console
2. Copy Account SID and Auth Token

## 🚀 Deployment

### Railway (Recommended)

1. Push code to GitHub
2. Connect repo to Railway: https://railway.app
3. Add environment variables in Railway dashboard
4. Deploy automatically

### Heroku

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name
git push heroku main
```

### Render

1. Connect GitHub repo to https://render.com
2. Set environment variables
3. Deploy

## 📦 Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **django** - ORM and database
- **pydantic** - Data validation
- **python-dotenv** - Environment variables
- **twilio** - WhatsApp API
- **aiosmtplib** - Email notifications

## 🔒 Security

- ✅ `.env` is in `.gitignore` - Never commit secrets
- ✅ CORS enabled for production (modify as needed)
- ✅ Admin endpoints protected with secret key
- ✅ Email validation on contact form

## 📝 License

MIT License - feel free to use this for your own portfolio!

## 👨‍💻 Author

**Dishambha Awasthi**
- GitHub: https://github.com/dishambha
- LinkedIn: https://www.linkedin.com/in/dishambha-awasthi
- LeetCode: https://leetcode.com/u/dishambha_awasthi/
