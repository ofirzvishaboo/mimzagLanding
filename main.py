import asyncio
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated

load_dotenv()

GMAIL_USER     = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
TO_EMAIL       = "mimzag1@gmail.com"

app = FastAPI(title="ממזג")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

IMAGES_DIR = Path("static/images")
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".avif")


def find_image(name: str) -> str:
    """Search for `name` (no extension) in IMAGES_DIR. Returns URL or ''."""
    for ext in EXTENSIONS:
        if (IMAGES_DIR / f"{name}{ext}").exists():
            return f"/static/images/{name}{ext}"
    return ""


def _scan_gallery(folder: Path, limit: int = 10) -> list[str]:
    """Return URLs for all images inside `folder`, sorted by name, up to `limit`."""
    if not folder.exists():
        return []
    files = sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONS
    )
    return [f"/static/images/gallery/{f.name}" for f in files[:limit]]


def _send_email(name: str, phone: str, email: str, service: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"פנייה חדשה מהאתר — {name}"
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL

    html_body = f"""
    <div dir="rtl" style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;
         background:#0a2416;color:#fff;border-radius:12px;overflow:hidden;">
      <div style="background:#1d5c3a;padding:24px 28px;">
        <h2 style="margin:0;font-size:1.3rem;">📩 פנייה חדשה מאתר ממזג</h2>
      </div>
      <div style="padding:28px;line-height:2;">
        <p><strong>שם מלא:</strong> {name}</p>
        <p><strong>טלפון:</strong> {phone}</p>
        <p><strong>אימייל:</strong> {email or '—'}</p>
        <p><strong>סוג שירות:</strong> {service or '—'}</p>
      </div>
      <div style="background:#123d26;padding:14px 28px;font-size:.8rem;color:#aaa;">
        נשלח אוטומטית מאתר ממזג
      </div>
    </div>
    """
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    images = {
        "hero":             find_image("hero-bg"),
        "logo":             find_image("logo"),
        "about":            find_image("about"),
        "service_shop":     find_image("service-shop"),
        "service_cocktail": find_image("service-cocktail"),
        "service_tasting":  find_image("service-tasting"),
        "gallery": _scan_gallery(IMAGES_DIR / "gallery", limit=10),
    }
    return templates.TemplateResponse(request=request, name="index.html", context={"images": images})


@app.post("/contact")
async def contact(
    name:    Annotated[str, Form()],
    phone:   Annotated[str, Form()],
    email:   Annotated[str, Form()] = "",
    service: Annotated[str, Form()] = "",
):
    print("--- פנייה חדשה ---")
    print(f"שם:     {name}")
    print(f"טלפון:  {phone}")
    print(f"אימייל: {email}")
    print(f"שירות:  {service}")
    print("------------------")

    if GMAIL_USER and GMAIL_PASSWORD:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _send_email, name, phone, email, service)
            print("✅ מייל נשלח בהצלחה")
        except Exception as e:
            print(f"⚠️  שגיאה בשליחת מייל: {e}")

    return JSONResponse({"success": True, "message": "תודה! נחזור אליך בהקדם."})
