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


# ── Ensure database tables exist on startup ────────────────────────────────────
@app.on_event("startup")
async def ensure_database():
    """Safety check: ensure database tables exist before serving requests."""
    try:
        # Run Django DB operations in a thread (Django requires sync context)
        await asyncio.to_thread(_init_database)
        print("[Startup] ✓ Database ready")
    except Exception as e:
        print(f"[Startup] ✗ Error ensuring database: {e}")
        raise


def _init_database():
    """Initialize database tables (synchronous function)."""
    from django.db import connection
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import User

    tables = connection.introspection.table_names()
    if "portfolio_contactmessage" not in tables:
        print("[Startup] Database tables missing! Creating...")
        with connection.schema_editor() as schema_editor:
            if "django_content_type" not in tables:
                schema_editor.create_model(ContentType)
            if "auth_user" not in tables:
                schema_editor.create_model(User)
            schema_editor.create_model(ContactMessage)
        print("[Startup] ✓ Database tables created successfully")
    else:
        print("[Startup] ✓ ContactMessage table already exists")


@app.get("/", response_class=FileResponse)
async def serve_portfolio():
    static_dir = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_dir)


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

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
