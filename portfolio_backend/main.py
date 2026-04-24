"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Dishambha Awasthi – Portfolio Backend
 Architecture: Django ORM + Models (database layer)
               FastAPI (API layer + WhatsApp/Email)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SETUP:
  pip install fastapi uvicorn django djangorestframework
              python-dotenv : The term 'python-dotenv' is not recognized as the name of a cmdlet, function, script file, or
operable program. Check the spelling of the name, or if a path was included, verify that the path is correct and try
again.
At line:2 char:15
+               python-dotenv twilio aiosmtplib pydantic
+               ~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (python-dotenv:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException


FOLDER STRUCTURE:
  portfolio_backend/
  ├── main.py            ← FastAPI entry point (this file)
  ├── .env               ← secrets (never commit!)
  ├── django_setup.py    ← Django bootstrap
  ├── models.py          ← Django ORM models
  ├── static/
  │   └── index.html     ← Your portfolio HTML
  └── manage.py          ← Django management commands

RUN:
  python manage.py migrate   # create DB tables
  uvicorn main:app --reload  # start server
"""

# ════════════════════════════════════════════════
# 1.  django_setup.py  – bootstrap Django ORM
# ════════════════════════════════════════════════
"""
# django_setup.py
import django
from django.conf import settings
import os

def setup():
    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "portfolio"],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": "portfolio.db",          # swap for PostgreSQL in prod
                }
            },
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        django.setup()
"""

# ════════════════════════════════════════════════
# 2.  models.py  – Django ORM models (saved to DB)
# ════════════════════════════════════════════════
"""
# models.py  (place inside a Django app called 'portfolio')
from django.db import models

class ContactMessage(models.Model):
    MESSAGE_TYPES = [
        ("opportunity", "Job Opportunity"),
        ("project",     "Project Collaboration"),
        ("query",       "General Query"),
        ("review",      "Review / Feedback"),
        ("other",       "Other"),
    ]
    name        = models.CharField(max_length=120)
    email       = models.EmailField()
    msg_type    = models.CharField(max_length=20, choices=MESSAGE_TYPES, default="query")
    subject     = models.CharField(max_length=200, blank=True)
    message     = models.TextField()
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    notified_wa = models.BooleanField(default=False)  # WhatsApp sent?
    notified_em = models.BooleanField(default=False)  # Email sent?

    class Meta:
        ordering = ["-created_at"]
        app_label = "portfolio"

    def __str__(self):
        return f"[{self.msg_type}] {self.name} – {self.subject[:40]}"
"""

# ════════════════════════════════════════════════
# 3.  main.py  – FastAPI application
# ════════════════════════════════════════════════

import os, asyncio
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()  # loads .env file

# ── Django ORM setup (runs before first import of models) ─────────────────────
import django_setup

django_setup.setup()
from models import ContactMessage  # Django ORM model

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(title="Dishambha Portfolio API", version="2.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def serve_portfolio():
    return FileResponse("static/index.html")


# ── ENV VARIABLES  (.env file) ─────────────────────────────────────────────────
# Create a .env file with these values:
#
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=dishambhaawasthi0131@gmail.com
# SMTP_PASS=your_16char_gmail_app_password
#
# TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# TWILIO_TOKEN=your_auth_token
# TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  (Twilio sandbox number)
# MY_WHATSAPP=whatsapp:+919369879498
#
# ADMIN_SECRET=your_secret_key_for_admin_routes

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MY_EMAIL = "dishambhaawasthi0131@gmail.com"

TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
MY_WA = os.getenv("MY_WHATSAPP", "whatsapp:+919369879498")

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change_me_in_prod")


# ── Pydantic schema ────────────────────────────────────────────────────────────
class ContactIn(BaseModel):
    name: str
    email: EmailStr
    type: str = "query"
    subject: str = ""
    message: str


# ── WhatsApp via Twilio ────────────────────────────────────────────────────────
async def send_whatsapp(body: str):
    """Send WhatsApp message via Twilio API."""
    if not TWILIO_SID:
        print("[WhatsApp] Twilio not configured – skipping.")
        return False
    try:
        from twilio.rest import Client

        client = Client(TWILIO_SID, TWILIO_TOKEN)
        msg = client.messages.create(body=body, from_=TWILIO_FROM, to=MY_WA)
        print(f"[WhatsApp] Sent: {msg.sid}")
        return True
    except Exception as e:
        print(f"[WhatsApp] Error: {e}")
        return False


# ── Email via aiosmtplib ───────────────────────────────────────────────────────
async def send_email(name: str, email: str, msg_type: str, subject: str, message: str):
    """Send email notification to Dishambha."""
    if not SMTP_USER:
        print("[Email] SMTP not configured – skipping.")
        return False
    try:
        mail = MIMEMultipart("alternative")
        mail["Subject"] = f"[Portfolio] {msg_type.upper()}: {subject or 'New Contact'}"
        mail["From"] = SMTP_USER
        mail["To"] = MY_EMAIL
        body = f"""
New message from your portfolio!

From    : {name} <{email}>
Type    : {msg_type}
Subject : {subject}
Time    : {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

Message:
{message}
        """.strip()
        mail.attach(MIMEText(body, "plain"))
        async with aiosmtplib.SMTP(
            hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True
        ) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASS)
            await smtp.send_message(mail)
        print("[Email] Sent successfully.")
        return True
    except Exception as e:
        print(f"[Email] Error: {e}")
        return False


# ── API Routes ─────────────────────────────────────────────────────────────────
@app.post("/api/contact")
async def contact(data: ContactIn, request: Request):
    """Save message to Django ORM (SQLite/PostgreSQL) and notify via WA + email."""
    # 1. Save to database using Django ORM
    msg_obj = await asyncio.to_thread(
        ContactMessage.objects.create,
        name=data.name,
        email=data.email,
        msg_type=data.type,
        subject=data.subject,
        message=data.message,
        ip_address=request.client.host,
    )

    # 2. Fire notifications concurrently (non-blocking)
    wa_text = (
        f"📩 *New Portfolio Message!*\n"
        f"From: {data.name} ({data.email})\n"
        f"Type: {data.type}\n"
        f"Subject: {data.subject}\n\n"
        f"{data.message[:300]}"
    )
    wa_ok, em_ok = await asyncio.gather(
        send_whatsapp(wa_text),
        send_email(data.name, data.email, data.type, data.subject, data.message),
    )

    # 3. Update notification flags
    await asyncio.to_thread(
        lambda: ContactMessage.objects.filter(pk=msg_obj.pk).update(
            notified_wa=wa_ok, notified_em=em_ok
        )
    )

    return {
        "status": "success",
        "message": "Thanks! I'll get back to you within 24 hours.",
        "id": msg_obj.pk,
    }


@app.get("/api/portfolio")
async def get_portfolio():
    return JSONResponse(
        {
            "name": "Dishambha Awasthi",
            "email": MY_EMAIL,
            "phone": "+91 9369879498",
            "github": "https://github.com/dishambha",
            "linkedin": "https://www.linkedin.com/in/dishambha-awasthi",
            "leetcode": "https://leetcode.com/u/dishambha_awasthi/",
        }
    )


@app.get("/api/messages")
async def get_messages(secret: str = ""):
    """Admin endpoint – protect with secret key."""
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    msgs = await asyncio.to_thread(lambda: list(ContactMessage.objects.values()))
    return msgs


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# ════════════════════════════════════════════════
# 4.  .env template (create this file manually)
# ════════════════════════════════════════════════
"""
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dishambhaawasthi0131@gmail.com
SMTP_PASS=xxxx_xxxx_xxxx_xxxx   # Gmail App Password (not your login password!)

TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
MY_WHATSAPP=whatsapp:+919369879498

ADMIN_SECRET=make_this_random_and_long
"""

# ════════════════════════════════════════════════
# 5.  requirements.txt
# ════════════════════════════════════════════════
"""
fastapi==0.111.0
uvicorn[standard]==0.29.0
django==5.0.6
djangorestframework==3.15.1
python-dotenv==1.0.1
twilio==9.0.5
aiosmtplib==3.0.1
pydantic[email]==2.7.1
"""
