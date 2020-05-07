import smtplib
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .email_credentials import email, pwd


def send_mail(email_id, subject, message):
    me = email
    my_password = pwd
    you = email_id

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = me
    msg["To"] = you

    html = message
    part2 = MIMEText(html, "html")

    msg.attach(part2)

    s = smtplib.SMTP_SSL("smtp.gmail.com")
    s.login(me, my_password)

    s.sendmail(me, you, msg.as_string())
    s.quit()


def medicine_available(email_id, details, medicines):
    subject = "Request for medicine {}".format(medicine)
    message = "<html><body>The medicine {} you requested is available at the pharmacy {} located in {}.</body></html>".format(
        medicine, details[0], details[1]
    )
    send_mail(email_id, subject, message)

def send_verification_mail(authority_details):
    super_admin_email_list = [
        "sakshiuppor@gmail.com",
        "shahsaakshi25@gmail.com",
        #"sanketyou8@gmail.com",
        #"",
        #"",
    ]

    subject = "New Authority Sign-Up"
    message = """
    <html>
        <body>
            <p>Hi, {} just registered for the position of authority at Trana</p> 
            Details:
            """.format(details.get('name'))

    for detail in details:
        message += """
        <br>
        <b> {}: </b> {}""".format(detail, details[detail])

    message += """
        <br>
        <a href="{% url 'verify' %}"><button class="green-sec">Approve</button></a>
        <a href="{% url 'verify' %}"><button class="green-sec">Reject</button></a>
        </body>
    </html>"""
    
    for mail in super_admin_email_list:
        send_mail(mail, subject, message)

def send_result(email_id, user, accepted):
    if accepted == 'True':
        subject = "Authority Account Application Verified"
        message = """<html><body>You can now log in to your authority dashboard.
        <br>
        <b>Email ID:</b> {}
        <br>
        <b>Password:</b> {}
        
        <html><body>""".format(user.get("email"), user.get("password"))
        send_mail(email_id, subject, message)

    else:
        subject = "Authority Account Application Rejected"
        message = """<html><body>Your application for the position of authority at Trana has been rejected.
        <html><body>"""
        send_mail(email_id, subject, message)
    