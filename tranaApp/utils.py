import smtplib
import math
import yagmail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .email_credentials import email, pwd

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

def send_mail(to, subject, message):
    """me = email
    my_password = pwd
    you = email_id

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = me
    msg["To"] = you

    html = message
    part2 = MIMEText(html, "html")

    msg.attach(part2)
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()
    server.login(me, my_password)

    server.sendmail(me, you, msg.as_string())
    server.quit()"""

    yag = yagmail.SMTP('medtrana2020','covidproject2020')
    yag.send(to = to, subject = subject, contents = message)


def medicine_available(email_id, details, medicines):
    subject = "Request for medicine {}".format(medicine)
    message = "<html><body>The medicine {} you requested is available at the pharmacy {} located in {}.</body></html>".format(
        medicine, details[0], details[1]
    )
    send_mail(email_id, subject, message)

def send_verification_mail(request, details):
    current_site = get_current_site(request)

    super_admin_email_list = [
        "sakshiuppoor@gmail.com",
        #"phani.lav@gmail.com",
        #"medtrana2020@gmail.com",
        #"shahsaakshi25@gmail.com",
        #"sanketyou8@gmail.com",
        #"",
        #"",
    ]
    print("~~~~~~~~~~~~",type(details["uId"]), type('True'))
    subject = "New Authority Sign-Up"
    message = render_to_string("verification_mail.html",
    {
        "domain":current_site.domain,
        "details":details,
    })

    send_mail(super_admin_email_list, subject, message)

def send_result(email_id, user, accepted):
    print(user)
    #print(user.to_dict())
    print(user.__dict__)
    if accepted == 'True':
        subject = "Authority Account Application Verified"
        message = """<html><body>You can now log in to your authority dashboard.
        <br>
        <b>Email ID:</b> {}
        <br>
        <html><body>""".format(email_id)
        print(message)
        send_mail(email_id, subject, message)

    else:
        subject = "Authority Account Application Rejected"
        message = """<html><body>Your application for the position of authority at Trana has been rejected.
        <html><body>"""
        send_mail(email_id, subject, message)
