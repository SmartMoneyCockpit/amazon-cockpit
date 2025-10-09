import os, io, csv, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import date, timedelta
import pandas as pd

from services.amazon_ads_service import fetch_metrics

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_TO = os.getenv("VEGA_EMAIL_TO","").split(",")
EMAIL_FROM = os.getenv("VEGA_EMAIL_FROM","noreply@vega.local")

def send_email(subject, html, attachment_name=None, attachment_bytes=None):
    if SENDGRID_API_KEY:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
            message = Mail(from_email=EMAIL_FROM, to_emails=EMAIL_TO, subject=subject, html_content=html)
            if attachment_bytes and attachment_name:
                import base64
                encoded = base64.b64encode(attachment_bytes).decode()
                att = Attachment(FileContent(encoded), FileName(attachment_name), FileType("text/csv"), Disposition("attachment"))
                message.attachment = att
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            return True
        except Exception as e:
            print("SendGrid error:", e)

    # Fallback SMTP
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg.attach(MIMEText(html, "html"))
    if attachment_bytes and attachment_name:
        part = MIMEApplication(attachment_bytes, Name=attachment_name)
        part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
        msg.attach(part)
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    return True

def run_daily(days=7):
    end = date.today()
    start = end - timedelta(days=days-1)
    rows = fetch_metrics(start, end, which=("SP","SB","SD"), persist=True)
    df = pd.DataFrame(rows)
    if not df.empty:
        for col in ["impressions","clicks","cost","sales14d","purchases14d"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        total_imp = int(df.get("impressions", pd.Series([0])).sum())
        total_clk = int(df.get("clicks", pd.Series([0])).sum())
        total_cost = float(df.get("cost", pd.Series([0])).sum())
        total_sales = float(df.get("sales14d", pd.Series([0])).sum())
        roas = (total_sales/total_cost) if total_cost>0 else None

        html = f"""
        <h3>Vega Amazon Ads Digest ({start} → {end})</h3>
        <ul>
          <li>Impressions: {total_imp:,}</li>
          <li>Clicks: {total_clk:,}</li>
          <li>Cost: ${total_cost:,.2f}</li>
          <li>Sales (14d): ${total_sales:,.2f}</li>
          <li>RoAS: {f"{roas:,.2f}×" if roas else "—"}</li>
        </ul>
        """
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        send_email("Vega Ads Digest", html, "vega_ads_metrics.csv", csv_bytes)
    else:
        send_email("Vega Ads Digest (no data)", f"<p>No rows for {start} → {end}.</p>")

if __name__ == "__main__":
    run_daily(days=int(os.getenv("VEGA_DIGEST_DAYS","7")))