import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buildPayload(task, state):
    payload = f"| Task | State |\n|------|-------|\n| {task} | {state} |\n"
    return payload

def sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password):
    try:
        # Create a MIMEText object to represent the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the message as plain text
        msg.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error: {e}")


