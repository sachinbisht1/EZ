import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(to_email, subject, body, attachment_path=None):
    """
    Send an email using Gmail SMTP.
    
    Args:
        to_email (str): Recipient's email address.
        subject (str): Email subject.
        body (str): Email body text.
        attachment_path (str): Path to the file to attach (optional).
    """
    try:
        # Gmail SMTP server credentials
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = "ksachinbisht@gmail.com"  # Replace with your Gmail
        from_password = "kjsh iiwa xemd itud"  # Replace with your password or app-specific password
        
        # Set up the email components
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach file if provided
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_path.split("/")[-1]}',
            )
            msg.attach(part)

        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(from_email, from_password)

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Example usage
if __name__ == "__main__":
    send_email(
        to_email="ksachinbisht@gmail.com",
        subject="Test Email",
        body="This is a test email sent using Gmail SMTP.",
        attachment_path="/home/sachin/Documents/EZ/requirements.txt"  # Replace or set to None if no attachment
    )
