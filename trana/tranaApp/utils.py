import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .pwd import pwd


def send_mail(email_id):
    me = "variegatedlark@gmail.com"
    my_password = pwd
    you = email_id

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Alert"
    msg["From"] = me
    msg["To"] = you

    html = "<html><body><p>Hi, I have the following alerts for you!</p></body></html>"
    part2 = MIMEText(html, "html")

    msg.attach(part2)

    s = smtplib.SMTP_SSL("smtp.gmail.com")
    s.login(me, my_password)

    s.sendmail(me, you, msg.as_string())
    s.quit()
