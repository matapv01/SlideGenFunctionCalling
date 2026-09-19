"""SMTP delivery for short-lived email verification codes."""

from email.message import EmailMessage
import smtplib

from backend.config import (
    AUTH_OTP_EXPIRE_MINUTES,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
    SMTP_USERNAME,
)


class EmailDeliveryError(RuntimeError):
    """Raised when the configured SMTP server cannot deliver a message."""


def send_verification_code(recipient: str, code: str) -> None:
    """Send a login verification code using the configured SMTP server."""
    if not SMTP_HOST or not SMTP_FROM_EMAIL:
        raise EmailDeliveryError(
            "Email verification is not configured. Set SMTP_HOST and SMTP_FROM_EMAIL."
        )

    message = EmailMessage()
    message["Subject"] = "Your Slidegen sign-in code"
    message["From"] = f"Slidegen <{SMTP_FROM_EMAIL}>"
    message["To"] = recipient
    message["Auto-Submitted"] = "auto-generated"
    message["X-Auto-Response-Suppress"] = "All"
    message.set_content(
        "Your Slidegen sign-in code\n\n"
        f"{code}\n\n"
        f"This code expires in {AUTH_OTP_EXPIRE_MINUTES} minutes.\n"
        "If you did not request this code, you can safely ignore this email.\n\n"
        "— Slidegen"
    )
    message.add_alternative(
        f"""
        <!doctype html>
        <html lang="en">
          <body style="margin:0;background:#f5f5f2;color:#202020;font-family:Arial,sans-serif;">
            <div style="max-width:520px;margin:32px auto;padding:32px;background:#fffefa;border:1px solid #e1e0d9;border-radius:10px;">
              <p style="margin:0 0 24px;color:#b65f4c;font-size:12px;font-weight:700;letter-spacing:2px;">SLIDEGEN</p>
              <h1 style="margin:0 0 12px;font-size:24px;font-weight:600;">Your sign-in code</h1>
              <p style="margin:0 0 24px;color:#666861;font-size:15px;line-height:1.5;">Enter this code to finish signing in to your Slidegen account.</p>
              <div style="margin:0 0 24px;padding:18px;text-align:center;background:#f1f0ea;border-radius:8px;color:#202020;font-size:30px;font-weight:700;letter-spacing:8px;">{code}</div>
              <p style="margin:0;color:#777872;font-size:13px;line-height:1.5;">This code expires in {AUTH_OTP_EXPIRE_MINUTES} minutes. If you did not request it, you can safely ignore this email.</p>
            </div>
          </body>
        </html>
        """,
        subtype="html",
    )

    smtp_class = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP
    try:
        with smtp_class(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                server.starttls()
            if SMTP_USERNAME:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("The verification email could not be sent.") from exc
