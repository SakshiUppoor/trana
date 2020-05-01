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

# from .utils import send_mail

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
        print(current_user)
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
        return user.to_dict().get("pharmacy-name"), user.to_dict().get("address")
    return None


def get_components(collection):
    reports_ref = db.collection(collection)
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        if report.to_dict().get("resolved") != True:
            if report.to_dict().get("location"):
                co_list.append(
                    [report.to_dict()["location"][0], report.to_dict()["location"][1]]
                )
            entry = {}
            entry["id"] = report.id
            if report.to_dict().get("uId"):
                uId = report.to_dict().get("uId")
                entry["name"] = getName(uId)
            for field in report.to_dict():
                entry[field] = report.to_dict()[field]
            print(entry)
            reports_list.append(entry)
    return co_list, reports_list


#############################################
#       AUTHENTICATION & LOGIN STUFF        #
#############################################


def signup(request):
    if request.method == "POST":
        name = request.POST.get(u"name")
        email = request.POST.get(u"email")
        position = "user"
        password1 = request.POST.get(u"password1")
        password2 = request.POST.get(u"password2")

        if password1 == password2:
            try:
                email_ref = firebase_admin.auth.get_user_by_email(email, app=None)
                messages.info(request, "Your account already exists")
                return redirect("login")
            except:
                user = firebase_admin.auth.create_user(email=email, password=password2)
                uid = user.uid
                data = {u"name": name, u"position": position, u"email": email}
                db.collection(u"Users").document(uid).set(data)
        else:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if position == "pharmacist":
            pharmacy_name = request.POST.get(u"pharmacy-name")
            address = request.POST.get(u"address")
            data[u"pharmacy-name"] = pharmacy_name
            data[u"address"] = address
        db.collection(u"Users").document(uid).set(data)

        current_user = authe.sign_in_with_email_and_password(email, password2)
        # current_user_uid = current_user["localId"]
        session_id = current_user["idToken"]
        request.session["uid"] = str(session_id)

        position = getPosition(request)
        print(position)
        if position == "authority":
            print("hello")
            return HttpResponseRedirect(reverse("reports"))
        elif position == "pharmacist":
            return HttpResponseRedirect(reverse("medicines"))
        elif position == "user":
            return HttpResponseRedirect(reverse("users"))
        else:
            return HttpResponseRedirect(reverse("users"))

    return render(request, "signup.html", {"title": "signup"})


def login_view(request):
    if getPosition(request) != "user":
        if request.method == "POST":
            email = request.POST["email"]
            password = request.POST["password"]
            try:
                current_user = authe.sign_in_with_email_and_password(email, password)
                request.session["current_user"] = current_user
                # current_user_uid = current_user["localId"]
                session_id = current_user["idToken"]
                request.session["uid"] = str(session_id)
                print(request.__dict__)
                position = getPosition(request)
                print(position)
                if position == "authority":
                    print("hello")
                    return HttpResponseRedirect(reverse("reports"))
                elif position == "pharmacist":
                    return HttpResponseRedirect(reverse("medicines"))
                elif position == "user":
                    return HttpResponseRedirect(reverse("users"))
                else:
                    return HttpResponseRedirect(reverse("users"))
            except Exception as e:
                print(e)
                messages.error(request, "Invalid credentials")
                return render(request, "login.html")
        return render(request, "login.html", {"title": "login"})
    return redirect("users")


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("login"))


#############################################
#                DASHBOARDS                 #
#############################################


def reportsDashboard(request):
    if getPosition(request) != None:
        if getPosition(request) == "authority":
            co_list, reports_list = get_components("Reports")
            context = {
                "co_list": co_list,
                "reports": reports_list,
            }
            return render(request, "reports.html", context)
        else:
            return HttpResponseRedirect(reverse("404"))
    return HttpResponseRedirect(reverse("login"))


def medicinesDashboard(request):
    if getPosition(request) != None:
        if getPosition(request) == "pharmacist":
            co_list, medicines_list = get_components("Medicines")
            context = {
                "co_list": co_list,
                "medicines": medicines_list,
            }
            return render(request, "medicines.html", context)
        else:
            return HttpResponseRedirect(reverse("404"))
    return HttpResponseRedirect(reverse("login"))


def usersDashboard(request):
    # if getPosition(request) != None:
    #    return render(request, "appuser.html")
    print(getPosition(request))
    if getPosition(request) == "user":
        current_user = request.session.get("current_user")
        uid = current_user["localId"]
        report_ref = db.collection(u"Reports").where(u"uId", u"==", uid).stream()
        reports_list = []
        for report in report_ref:
            print(u"Document data: {}".format(report.to_dict()))
            get_report = report.to_dict()
            get_report["id"] = report.id
            del get_report["uId"]
            reports_list.append(get_report)

        med_ref = db.collection(u"Medicines").where(u"uId", u"==", uid).stream()
        meds_list = []
        for med in med_ref:
            print(u"Document data: {}".format(med.to_dict()))
            get_med = med.to_dict()
            get_med["id"] = med.id
            del get_med["uId"]
            meds_list.append(get_med)
        context = {
            "meds": meds_list,
            "reports": reports_list,
        }
        return render(request, "user.html", context)
    return HttpResponseRedirect(reverse("login"))


def notify(request, id):
    current_user = request.session["current_user"]
    med_ref = db.collection(u"Medicines").document(id)
    med_ref.set({u"resolved": True}, merge=True)
    medicine = med_ref.get().to_dict().get("medicine")
    uId = med_ref.get().to_dict().get("uId")
    user = firebase_admin.auth.get_user(uId)
    print(user.email)
    send_mail(user.email, getPharmacyDetails(current_user["localId"]), medicine)
    return HttpResponseRedirect(reverse("medicines"))


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
    return render(request, "404.html")


def reportCondition(request):
    if request.method == "POST":
        patient = request.POST.get(u"patient")
        address = request.POST.get(u"address")
        contact = request.POST.get(u"contact")
        age = request.POST.get(u"age")
        gender = request.POST.get(u"gender")
        case = request.POST.get(u"case")
        condition = request.POST.get(u"condition")
        treatment = request.POST.get(u"treatment")
        area = request.POST.get(u"area")
        info = request.POST.get(u"info")
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
        }
        if (
            type(request.POST.get(u"lat")) != str
            and type(request.POST.get(u"lon")) != str
        ):
            location = [
                float(request.POST.get(u"lat")),
                float(request.POST.get(u"lon")),
            ]
            data[u"location"] = location
        db.collection(u"Reports").document().set(data)
        return redirect("users")
    return render(request, "condition.html")


def orderMedicine(request):
    if request.method == "POST":
        contact = request.POST.get(u"contact")
        address = request.POST.get(u"address")
        medicine = request.POST.get(u"medicine")
        gender = request.POST.get(u"gender")
        age = request.POST.get(u"age")
        hospital = request.POST.get(u"hospital")
        doctor = request.POST.get(u"doctor")
        info = request.POST.get(u"info")
        area = request.POST.get(u"area")

        location = [
            float(request.POST.get(u"lat")),
            float(request.POST.get(u"lon")),
        ]
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
            u"location": location,
            u"age": age,
            u"gender": gender,
            u"hospital": hospital,
            u"doctor": doctor,
            u"area": area,
            u"description": info,
        }
        db.collection(u"Medicines").document(str(count)).set(data)

        return redirect("users")
    return render(request, "ordermeds.html")


#####################
#       HOME        #
#####################


def landing(request):
    return render(request, "landing.html", {"title": "landing"})
