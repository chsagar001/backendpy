import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import jwt
import random
from auth import SECRET_KEY, ALGORITHM

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "reachenddev@gmail.com"
SMTP_PASSWORD = "skim nibz demn pthb"
FROM_EMAIL = "reachendev@gmail.com"

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())


def generate_password_reset_token(email: str):
    expires_delta = timedelta(minutes=15)
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Function to generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))
