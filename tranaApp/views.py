from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

from django.contrib import messages
from django.contrib import auth

import firebase
from firebase import firebase
import pyrebase

from .utils import *

# from .utils import send_mail

import socket
socket.getaddrinfo('127.0.0.1', 8080)

###########################
# FIRESTORE CONFIGURATION #
###########################

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "ServiceAccountKey.json")
)
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()


current_user_uid = ""

##########################
# PYREBASE CONFIGURATION #
##########################

config = {
    "apiKey": "AIzaSyBybJho0cdp9_nQzX_eT3arRl2jIHNgyU4",
    "authDomain": "tra1-bfac8.firebaseapp.com",
    "databaseURL": "https://tra1-bfac8.firebaseio.com",
    "projectId": "tra1-bfac8",
    "storageBucket": "tra1-bfac8.appspot.com",
    "messagingSenderId": "404257539306",
    "appId": "1:404257539306:web:5c266442fe78892bde0393",
    "measurementId": "G-1FLRML6GY5",
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()

#############
#   UTILS   #
#############


def getPosition(request):
    if "current_user" in request.session:
        current_user = request.session["current_user"]
        # print(current_user)
        user_ref = db.collection(u"Users").document(current_user["localId"])
        user = user_ref.get()
        if user.exists:
            return user.to_dict().get("position")
    return None


def getName(uId):
    user_ref = db.collection(u"Users").document(uId)
    user = user_ref.get()
    if user.exists:
        print(user.to_dict().get("name"))
        return user.to_dict().get("name")
    return None


def getPharmacyDetails(uId):
    user_ref = db.collection(u"Users").document(uId)
    user = user_ref.get()
    if user.exists:
        print(user.id)
        # print(user.to_dict())
        return user.to_dict().get("pharmacy-name"), user.to_dict().get("address")
    return None

    
def get_components(collection):
    reports_ref = db.collection(collection)
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        if report.to_dict().get("resolved") != True and report.to_dict().get("uId"):
            entry = {}
            entry["id"] = report.id
            if report.to_dict().get("uId"):
                uId = report.to_dict().get("uId")
                entry["name"] = getName(uId)
            for field in report.to_dict():
                entry[field] = report.to_dict()[field]
            # print(entry)
            if report.to_dict().get("location"):
                co_list.append(
                    [report.to_dict()["location"][0], report.to_dict()["location"][1]]
                )
                entry["location"] = [
                    report.to_dict()["location"][0],
                    report.to_dict()["location"][1],
                ]
            reports_list.append(entry)
    return co_list, reports_list


#############################################
#       AUTHENTICATION & LOGIN STUFF        #
#############################################


def signup(request):
    if request.method == "POST":
        name = request.POST.get(u"name")
        email = request.POST.get(u"email")
        position = request.POST.get(u"position")
        password1 = request.POST.get(u"password1")
        password2 = request.POST.get(u"password2")

        if password1 == password2:
            try:
                email_ref = firebase_admin.auth.get_user_by_email(email)
                messages.info(request, "Your account already exists")
                return redirect("login")
            except Exception as e:
                print("hiiiiiii",e)
                user = firebase_admin.auth.create_user(email=email, password=password2)
                uid = user.uid
                data = {u"name": name, u"position": position, u"email": email}
                db.collection(u"Users").document(uid).set(data)
        else:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if position == "pharmacist":
            phname = request.POST.get(u"phname")
            code = request.POST.get(u"code")
            phone = request.POST.get(u"phone")
            pharmacy_name = request.POST.get(u"pharmacy-name")
            address = request.POST.get(u"address")
            registration = request.POST.get(u"registration")
            data[u"pharmacist-name"] = phname
            data[u"pharmacy-name"] = pharmacy_name
            data[u"address"] = address
            data[u"code"] = code
            data[u"contact-number"] = phone
            data[u"registration"] = registration

        if position == "authority":
            auname = request.POST.get(u"auname")
            designation = request.POST.get(u"designation")
            organisation = request.POST.get(u"organisation")
            offadd = request.POST.get(u"offadd")
            phone = request.POST.get(u"offphone")
            data[u"authority-name"] = auname
            data[u"designation"] = designation
            data[u"organisation"] = organisation
            data[u"office-address"] = offadd
            data[u"contact-number"] = phone

        if position == "doctor":
            drname = request.POST.get(u"drname")
            drtype = request.POST.get(u"drtype")
            drworkplace = request.POST.get(u"drworkplace")
            drwpadd = request.POST.get(u"drwpadd")
            drwpphone = request.POST.get(u"drwpphone")
            data[u"doctor-name"] = drname
            data[u"doctor-type"] = drtype
            data[u"dr-workplace"] = drworkplace
            data[u"dr-workplace-address"] = drwpadd
            data[u"dr-workplace-phone"] = drwpphone
            if request.POST.get(u"lat") != "" and request.POST.get(u"lon") != "":
                location = [
                    float(request.POST.get(u"lat")),
                    float(request.POST.get(u"lon")),
                ]
                data[u"location"] = location
            db.collection(u"Users").document().set(data)
            # return render(request,'doctor.html')

        db.collection(u"Users").document(uid).set(data, merge=True)
        # print(uid)

        current_user = authe.sign_in_with_email_and_password(email, password2)
        request.session["current_user"] = current_user
        session_id = current_user["idToken"]
        request.session["uid"] = str(session_id)
        position = getPosition(request)
        # print(position)
        if position == "authority":
            # print("hello")
            data["uId"] = uid
            send_verification_mail(request, data)
            return HttpResponseRedirect(reverse("details"))
        elif position == "doctor":
            # print("doctor")
            data["uId"] = uid
            dr_send_verification_mail(request, data)
            return HttpResponseRedirect(reverse("details"))
        elif position == "pharmacist":
            return HttpResponseRedirect(reverse("medicines"))
        elif position == "user":
            return HttpResponseRedirect(reverse("users"))
        else:
            return HttpResponseRedirect(reverse("users"))

    return render(request, "signup.html", {"title": "signup"})


def login_view(request):
    print("Login~~~~~~~~~", getPosition(request))
    if getPosition(request) != "user":
        if request.method == "POST":
            if "reset" in request.POST:
                #messages.error(
                #    request, "Password reset linked has been sent to your mail."
                #)
                return render(request, "login.html", {"title": "login", "position":getPosition(request)})
            else:
                email = request.POST["email"]
                password = request.POST["password"]
                try:
                    firebase_admin.auth.get_user_by_email(email)
                    current_user = authe.sign_in_with_email_and_password(
                        email, password
                    )
                    # print("~~~~~~~~~~~",current_user['localId'])
                    request.session["current_user"] = current_user
                    session_id = current_user["idToken"]
                    request.session["uid"] = str(session_id)
                    #print(request.__dict__)
                    position = getPosition(request)
                    # print(position)
                    if position == "authority":
                        print("hello")
                        auth_ref = db.collection(u"Users").document(current_user["localId"])
                        approved = auth_ref.get().to_dict().get("approved")
                        if approved==True:
                            return HttpResponseRedirect(reverse("reports"))
                        else:
                            messages.error(request,'Your account is not yet verified')
                    elif position == "doctor":
                        # print("doctor")
                        auth_ref = db.collection(u"Users").document(current_user["localId"])
                        approved = auth_ref.get().to_dict().get("approved")
                        if approved==True:
                            return redirect('doctor')
                        else:
                            messages.error(request,'Your account is not yet verified')
                    elif position == "pharmacist":
                        return HttpResponseRedirect(reverse("medicines"))
                    elif position == "user":
                        return HttpResponseRedirect(reverse("users"))
                    elif position == "admin":
                        return HttpResponseRedirect(reverse("pending"))
                    else:
                        return HttpResponseRedirect(reverse("users"))
                except Exception as e:
                    print("!!!!!!!!!!!!!", e)
                    if type(e) == firebase_admin.auth.UserNotFoundError:
                        message = "Account doesn't exist."
                    else:
                        message = "Please check your password."
                    messages.error(request, message)
        print("K")
        return render(request, "login.html", {"title": "login", "position":getPosition(request)})
    return redirect("users")


def verify(request, uId, accepted):
    try:
        user_ref = db.collection(u"Users").document(uId)
        user = user_ref.get()
        email = user.to_dict().get("email")
        position = user.to_dict().get("position")
        user_instance = firebase_admin.auth.get_user_by_email(email)
        # print(user_instance)
        if user.to_dict().get("approved") == True:
            accepted = "done"
            return render(request,'verify.html',{"title":"verify", "accepted":accepted,"position":position})

        send_result(email, user_instance, accepted,position)
        if accepted == 'True':
            db.collection(u"Users").document(uId).set({'approved':True}, merge=True)
        else:
            db.collection(u"Users").document(uId).delete()
            firebase_admin.auth.delete_user(uId)
            context={"title":verify,"accepted":accepted}
    except:
        accepted = "done"
    return render(request,'verify.html',{"title":"verify", "accepted":accepted, "position":position})

def reset_password(request):
    return render(request, "forgot_password.html", {'title':'reset'})


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("login"))


#############################################
#                DASHBOARDS                 #
#############################################


def reportsDashboard(request):
    print("Reports~~~~~~~~~", request.session.get("uid"))
    if getPosition(request) != None:
        if getPosition(request) == "authority":
            co_list, reports_list = get_components("Reports")
            context = {
                "co_list": co_list,
                "reports": reports_list,
            }
            return render(request, "authority_dash.html", context)
        else:
            return redirect("404")
    return redirect("login")

def details(request):
    return render(request,"details.html", {"title":"details"})

def medicinesDashboard(request):
    if getPosition(request) != None:
        if getPosition(request) == "pharmacist":
            co_list, medicines_list = get_components("Medicines")
            context = {
                "co_list": co_list,
                "meds": medicines_list,
            }
            return render(request, "pharmacy_dash.html", context)
        else:
            return HttpResponseRedirect(reverse("404"))
    return HttpResponseRedirect(reverse("login"))


def usersDashboard(request):
    print(getPosition(request))
    print(getPosition(request))
    if getPosition(request) == "user":
        current_user = request.session.get("current_user")
        uid = current_user["localId"]
        report_ref = db.collection(u"Reports").where(u"uId", u"==", uid).stream()
        reports_list = []
        for report in report_ref:
            # print(u"Document data: {}".format(report.to_dict()))
            get_report = report.to_dict()
            get_report["id"] = report.id
            del get_report["uId"]
            reports_list.append(get_report)

        med_ref = db.collection(u"Medicines").where(u"uId", u"==", uid).stream()
        meds_list = []
        for med in med_ref:
            # print(u"Document data: {}".format(med.to_dict()))
            get_med = med.to_dict()
            get_med["id"] = med.id
            del get_med["uId"]
            meds_list.append(get_med)
        context = {
            "meds": meds_list,
            "reports": reports_list,
            "title":"users"
        }
        return render(request, "user.html", context)
    return HttpResponseRedirect(reverse("login"))


def notify(request, id):
    # try:
    current_user = request.session["current_user"]
    med_ref = db.collection(u"Medicines").document(id)
    med_ref.set({u"resolved": True}, merge=True)
    medicine = med_ref.get().to_dict().get("medicine")
    uId = med_ref.get().to_dict().get("uId")
    user = firebase_admin.auth.get_user(uId)
    # print(user.email)
    send_mail(user.email, getPharmacyDetails(current_user["localId"]), medicine)
    return HttpResponseRedirect(reverse("medicines"))
    #except Exception as e:
    #    print(e)
    #    return redirect("404")


def resolve(request, id):
    report_ref = db.collection(u"Reports").document(id)
    report_ref.set({u"resolved": True}, merge=True)
    return HttpResponseRedirect(reverse("reports"))


def getreport(request):
    if getPosition(request) != None:
        if getPosition(request) == "user":
            current_user = request.session.get("current_user")
            uid = current_user["localId"]
            report_ref = db.collection(u"Reports").where(u"uId", u"==", uid).stream()
            reports_list = []
            for report in report_ref:
                print(u"Document data: {}".format(report.to_dict()))
                get_report = report.to_dict()
                del get_report["uId"]
                reports_list.append(get_report)
            context = {
                "reports": reports_list,
                "reports_list": reports_list,
            }
            return render(request, "getreport.html", context)
        else:
            return HttpResponseRedirect(reverse("404"))
    return HttpResponseRedirect(reverse("login"))


def getmedicine(request):
    if getPosition(request) != None:
        if getPosition(request) == "user":
            co_list, reports_list = get_components("Medicines")
            current_user = request.session.get("current_user")
            uid = current_user["localId"]
            med_ref = db.collection(u"Medicines").where(u"uId", u"==", uid).stream()
            for med in med_ref:
                print(u"Medicine data: {}".format(med.to_dict()))
            get_med = med.to_dict()
            del get_med["uId"]
            del get_med["url"]
            context = {
                "co_list": co_list,
                "reports": reports_list,
                "get_med": get_med,
            }
            return render(request, "getmed.html", context)
        else:
            return HttpResponseRedirect(reverse("404"))
    return HttpResponseRedirect(reverse("login"))


def page404(request):
    user = getPosition(request)
    context = {
        "user": user,
    }
    return render(request, "404.html", context)


def reportCondition(request):
    try:
        if request.method == "POST":
            patient = request.POST.get(u"patient")
            country = request.POST.get(u"country")
            hospitalAddress = request.POST.get(u"hospitalAddress")
            address = request.POST.get(u"address")
            contact = request.POST.get(u"contact")
            age = request.POST.get(u"age")
            gender = request.POST.get(u"gender")
            case = request.POST.get(u"case")
            condition = request.POST.get(u"condition")
            treatment = request.POST.get(u"treatment")
            area = request.POST.get(u"area")
            info = request.POST.get(u"info")
            print("!!!!", info)
            current_user = request.session.get("current_user")
            uid = current_user["localId"]

            abc = db.collection(u"Reports").get()
            list_items = []
            for i in abc:
                list_items.append(i)
            count = len(list_items) + 1
            data = {
                u"patient": patient,
                u"area": area,
                u"address": address,
                u"contact": contact,
                u"age": age,
                u"gender": gender,
                u"case": case,
                u"condition": condition,
                u"treatment": treatment,
                u"uId": uid,
                u"description": info,
                u"country": country,
                u"hospitalAddress": hospitalAddress,
            }
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lat"))
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lon"))
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lat") == "")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lon") == " ")

            if request.POST.get(u"lat") != "" and request.POST.get(u"lon") != "":
                location = [
                    float(request.POST.get(u"lat")),
                    float(request.POST.get(u"lon")),
                ]
                data[u"location"] = location
            db.collection(u"Reports").document().set(data)
            return redirect("users")
        return render(request, "condition.html")
    except Exception as e:
        print(e)
        return redirect("404")


def orderMedicine(request):
    try:
        if request.method == "POST":
            patient = request.POST.get(u"patient")
            country = request.POST.get(u"country")
            hospitalAddress = request.POST.get(u"hospitalAddress")
            contact = request.POST.get(u"contact")
            address = request.POST.get(u"address")
            medicine = request.POST.get(u"medicine")
            gender = request.POST.get(u"gender")
            age = request.POST.get(u"age")
            hospital = request.POST.get(u"hospital")
            doctor = request.POST.get(u"doctor")
            info = request.POST.get(u"info")
            area = request.POST.get(u"area")
            url = request.POST.get(u"url")
            current_user = request.session.get("current_user")
            uid = current_user["localId"]
            abc = db.collection(u"Medicines").get()
            list_items = []
            for i in abc:
                list_items.append(i)
            count = len(list_items) + 1
            data = {
                u"contact": contact,
                u"address": address,
                u"medicine": medicine,
                "url": url,
                u"uId": uid,
                u"age": age,
                u"gender": gender,
                u"hospital": hospital,
                u"doctor": doctor,
                u"area": area,
                u"description": info,
                u"patient": patient,
                u"country": country,
                u"hospitalAddress": hospitalAddress,
            }
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lat"))
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST.get(u"lon"))
            if request.POST.get(u"lat") != "" and request.POST.get(u"lon") != "":
                location = [
                    float(request.POST.get(u"lat")),
                    float(request.POST.get(u"lon")),
                ]
                data[u"location"] = location
            db.collection(u"Medicines").document().set(data)

            return redirect("users")
        return render(request, "ordermeds.html")
    except Exception as e:
        print(e)
        return redirect("404")

def consult(request):
    if request.method=='POST':
        current_user = request.session.get("current_user")                           
        uid = current_user["localId"]                                                                
        frm = db.collection(u"Users").document(uid).get().to_dict()                   
        sub = "Trana user " + frm.get(u"name") + " wants to contact you"        
        d_msg = request.POST['message'] 
        msg = """{} . To reply, mail on {}""".format(request.POST['message'], frm.get(u"email")) 
        data = {u"sender":frm.get(u"email"),u"message":d_msg}
        location = [
                request.POST.get(u"lat"),
                request.POST.get(u"lon")
        ]
        data[u"location"] = location
        mail_to =[] 
        dr_email = []
        doctors = db.collection(u"Users").where(u"position", u"==", "doctor").stream()
        if request.POST.get(u"lat") != "" and request.POST.get(u"lon") != "":
            lat = float(request.POST.get(u"lat"))
            lon = float(request.POST.get(u"lon"))
            for dr in doctors:
                dr = dr.to_dict()
                if dr.get("location"):
                    lat2 = dr["location"][0]
                    lon2 = dr["location"][1]
                    if isInRadius(lat,lon,float(lat2), float(lon2)):
                        mail_to.append(dr.get(u"email"))
                        print(dr.get(u"email"))
            if len(mail_to)>0 :
                send_mail(mail_to, sub, msg)
        else:
            for dr in doctors :
                mail_to.append(dr.get(u"email"))
            send_mail(mail_to, sub, msg)
        data[u"doctors"] = mail_to
        db.collection(u"Consultations").document().set(data)
        return redirect("users/")  
    return render(request,'doctor_consultation.html')


#####################
#       HOME        #
#####################


def landing(request):
    return render(request, "landing.html", {"title": "landing"})

def motivation(request):
    return render(request, "motivation.html", {"title": "motivation"})

def about(request):
    return render(request, "about.html", {"title": "about"})

def services(request):
    return render(request, "services.html", {"title": "services"})

def faq(request):
    return render(request, "faq.html", {"title": "faq"})

def contact(request):
    if request.method == "POST":
        name = request.POST.get(u"name")
        email = request.POST.get(u"email")
        subject = request.POST.get(u"subject")
        message = request.POST.get(u"message")
        data = {u"name": name, u"email": email, u"subject":subject,u"message":message}
        db.collection(u"Contact").document().set(data)
        send_contact_mail(request, data)

    return render(request, "contact.html", {"title": "contact"})

def doctor(request):
    return render(request,'doctor.html')

def pending(request):
    if getPosition(request) == 'admin':
        doc = []
        authy =[]
        users = db.collection(u"Users").stream()
        for user in users:
            # print("""!!!!!!!!!!!!!!!!!!!!! {}""".format(user.to_dict()))
            approved = user.to_dict().get("approved")
            if approved != True :
                id = user.id
                user = user.to_dict()
                user['id'] = id
                # print(user)
                if user.get("position") == 'doctor' :
                    doc.append(user)
                elif user.get("position") == 'authority' :
                    authy.append(user)
        print(doc)
        return render(request, 'p_users.html' , {'doctors':doc , 'authys' :authy})
    else:
        return redirect('login')

def approved(request):
    if getPosition(request) == 'admin':
        doc = []
        authy =[]
        pharma =[]
        u =[]
        admin =[]
        users = db.collection(u"Users").stream()
        for user in users:
            approved = user.to_dict().get("approved")
            if approved == True :
                id = user.id
                user = user.to_dict()
                user['id'] = id
                if user.get("position") == 'doctor' :
                    doc.append(user)
                elif user.get("position") == 'authority' :
                    authy.append(user) 
            else :
                id = user.id
                user = user.to_dict()
                user['id'] = id
                if user.get("position") == 'pharmacist':
                    pharma.append(user)
                elif user.get("position") == 'user':
                    u.append(user)
                elif user.get("position") == 'admin':
                    admin.append(user) 
        return render(request, 'ap_user.html' , {'doctors':doc , 'authys' :authy, 'users':u , 'pharmas':pharma, 'admins':admin})
    else:
        return redirect('login')

def statistics(request):
    if getPosition(request) == 'admin':
        user_ref = db.collection('Users').stream()
        reports = db.collection('Reports').stream()
        meds = db.collection('Medicines').stream()
        users = []
        pharmas =[]
        authys =[]
        drs =[]
        admins = []
        rep_resolved = []
        accidents1 =[]
        pregnancy1 = []
        terminal_illness1 = []
        post_operation1 = []
        accident_rec1 =[]
        child1 = []
        other1 = []
        rep_unresolved = []
        accidents2 =[]
        pregnancy2 = []
        terminal_illness2 = []
        post_operation2 = []
        accident_rec2 =[]
        child2= []
        other2 = []
        med_res =[]
        med_unres = []
        for u in user_ref:
            u = u.to_dict()
            if u.get('position') == 'user':
                users.append(u)
            elif u.get('position') == 'pharmacist':
                pharmas.append(u)
            elif u.get('position') == 'doctor' and u.get('approved') == True:
                drs.append(u)
            elif u.get('position') == 'authority' and u.get('approved') == True:
                authys.append(u)
            elif u.get('position') == 'admin':
                admins.append(u)
        for r in reports :
            r = r.to_dict()
            if r.get('resolved') == True:
                rep_resolved.append(r)
            else:
                rep_unresolved.append(r)
            for report in rep_resolved:
                if report.get('case') == 'Accident':
                    accidents1.append(report)
                elif report.get('case') == 'Pregnancy':
                    pregnancy1.append(report)
                elif report.get('case') == 'Terminal Illness':
                    terminal_illness1.append(report)
                elif report.get('case') == 'Post Operation':
                    post_operation1.append(report)
                elif report.get('case') == 'Accident Recovery':
                    accident_rec1.append(report)
                elif report.get('case') == 'Child':
                    child1.append(report)
                elif report.get('case') == 'Other':
                    other1.append(report)
            for report in rep_unresolved:
                if report.get('case') == 'Accident':
                    accidents2.append(report)
                elif report.get('case') == 'Pregnancy':
                    pregnancy2.append(report)
                elif report.get('case') == 'Terminal Illness':
                    terminal_illness2.append(report)
                elif report.get('case') == 'Post Operation':
                    post_operation2.append(report)
                elif report.get('case') == 'Accident Recovery':
                    accident_rec2.append(report)
                elif report.get('case') == 'Child':
                    child2.append(report)
                elif report.get('case') == 'Other':
                    other2.append(report)
        for med in meds:
            med = med.to_dict()
            if med.get('resolved') == True :
                med_res.append(med)
            else:
                med_unres.append(med)
        return render(request,'stats.html',{
            'users':users,
            'pharmas':pharmas,
            'authys':authys ,
            'drs':drs,
            'admins':admins,
            'accident1':accidents1,
            'pregnancy1':pregnancy1 ,
            'terminal_illness1':terminal_illness1,
            'post_operation1':post_operation1,
            'accident_rec1':accident_rec1,
            'child1':child1 ,
            'other1':other1 ,
            'accident2':accidents2,
            'pregnancy2':pregnancy2 ,
            'terminal_illness2':terminal_illness2,
            'post_operation2':post_operation2,
            'accident_rec2':accident_rec2,
            'child2':child2,
            'other2':other2 ,
            'med_res':med_res,
            'med_unres' :med_unres
        })
    else:
        return redirect('login')
