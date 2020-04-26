import smtplib
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .email_credentials import email, pwd


def send_mail(email_id, details, medicine):
    me = email
    my_password = pwd
    you = email_id

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Alert"
    msg["From"] = me
    msg["To"] = you

    html = "<html><body><p>Hi, I have the following alerts for you!</p> The medicine {} you requested is available at the pharmacy {} located in {}.</body></html>".format(
        medicine, details[0], details[1]
    )
    part2 = MIMEText(html, "html")

    msg.attach(part2)

    s = smtplib.SMTP_SSL("smtp.gmail.com")
    s.login(me, my_password)

    s.sendmail(me, you, msg.as_string())
    s.quit()
    
  def isInRadius(lat1,long1,lat2,long2):
    R = 6373.0
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    dlon = long2 - long1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    if distance<5000:
        return true
    else:
        return false
  
