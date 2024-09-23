import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def connectToSMTP(*, smtp_usr, smtp_passw):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    
    server = smtplib.SMTP(smtp_server, port) 
    server.starttls(context=context)
    server.login(smtp_usr, smtp_passw)
    
    return server

def sendMail(*, from_email, alias, to_email, body, subject, server): 
    msg = MIMEMultipart()
    msg['From'] = f"{alias}"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))    
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()