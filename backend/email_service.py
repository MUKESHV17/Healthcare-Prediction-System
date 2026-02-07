import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

# Configuration - Fetch from Environment Variables
# Users should export EMAIL_USER and EMAIL_PASS in their shell
REQUIRED_ENV_VARS = ["EMAIL_USER", "EMAIL_PASS"]

def get_email_credentials():
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    # Fallback for dev/demo purposes if variables aren't set
    # WARNING: Do not hardcode real credentials in production code artifacts
    return user, password

def send_email(to_email, subject, body, attachment_path=None):
    """
    Generic function to send an email with optional attachment.
    """
    user, password = get_email_credentials()
    
    if not user or not password:
        print("⚠️  Email skipping: EMAIL_USER or EMAIL_PASS environment variables not set.")
        return False

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    if attachment_path:
        try:
            if os.path.exists(attachment_path):
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)
            else:
                print(f"❌ Attachment not found: {attachment_path}")
        except Exception as e:
            print(f"❌ Failed to attach file: {e}")

    try:
        # Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def send_report_email(to_email, pdf_path, patient_name, disease_type):
    """
    Sends the generated PDF report to the user.
    """
    subject = f"Your {disease_type} Prediction Report - {patient_name}"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #009688;">Healthcare Prediction System</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>Please find attached your generated <strong>{disease_type} Prediction Report</strong>.</p>
            <p>This report includes your risk assessment and tailored recommendations.</p>
            <div style="background: #f1f1f1; padding: 10px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Note:</strong> This is an AI-generated assessment and does not replace professional medical advice.</p>
            </div>
            <p>Stay Healthy!</p>
            <br>
            <p>Best Regards,<br>AI Health Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body, pdf_path)

def send_appointment_email(to_email, details):
    """
    Sends an appointment confirmation email with details.
    """
    subject = f"Appointment Confirmed: Dr. {details['doctor_name']}"
    
    # Generate Google Maps Link if coords exist
    map_link = "#"
    if details.get('lat') and details.get('lng'):
        map_link = f"https://www.google.com/maps?q={details['lat']},{details['lng']}"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2196f3;">Appointment Confirmation</h2>
            <p>Hello,</p>
            <p>Your appointment has been successfully booked. Here are the details:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; font-weight: bold;">Doctor:</td>
                    <td style="padding: 10px;">Dr. {details['doctor_name']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; font-weight: bold;">Hospital:</td>
                    <td style="padding: 10px;">{details['hospital_name']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; font-weight: bold;">Date:</td>
                    <td style="padding: 10px;">{details['date']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; font-weight: bold;">Time:</td>
                    <td style="padding: 10px;">{details['time']}</td>
                </tr>
            </table>

            <p style="text-align: center; margin-top: 20px;">
                <a href="{map_link}" style="background-color: #2196f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Hospital Location</a>
            </p>

            <p>Please arrive 15 minutes before your scheduled time.</p>
            <br>
            <p>Best Regards,<br>Healthcare Prediction System</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)
