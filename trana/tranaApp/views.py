from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

from django.contrib import messages
from django.contrib import auth

from firebase import firebase
import pyrebase

from .utils import send_mail

###########################
# FIRESTORE CONFIGURATION #
###########################

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "ServiceAccountKey.json")
)
deafult_app = firebase_admin.initialize_app(cred)

db = firestore.client()

current_user = ""
current_user_uid = ""

##########################
# PYREBASE CONFIGURATION #
##########################

config = {
    "apiKey": "AIzaSyDXMensLWaA5AvH2M7r6DhR6oCIu1kXG5U",
    "authDomain": "trana-cfbcf.firebaseapp.com",
    "databaseURL": "https://trana-cfbcf.firebaseio.com",
    "projectId": "trana-cfbcf",
    "storageBucket": "trana-cfbcf.appspot.com",
    "messagingSenderId": "105597355531",
    "appId": "1:105597355531:web:b7d7645d90867fb34a690e",
    "measurementId": "G-FQ9WQ7Z7VQ",
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()

#############
#   UTILS   #
#############


def getPosition():
    if current_user_uid:
        user_ref = db.collection(u"Users").document(current_user_uid)
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
        position = request.POST.get(u"position")
        password = request.POST.get(u"password1")

        user = firebase_admin.auth.create_user(email=email, password=password)
        uid = user.uid
        data = {u"name": name, u"position": position}

        if position == "pharmacist":
            pharmacy_name = request.POST.get(u"pharmacy-name")
            address = request.POST.get(u"address")
            data[u"pharmacy-name"] = pharmacy_name
            data[u"address"] = address
        db.collection(u"Users").document(uid).set(data)

        global current_user, current_user_uid
        current_user = authe.sign_in_with_email_and_password(email, password)
        current_user_uid = current_user["localId"]
        session_id = current_user["idToken"]
        request.session["uid"] = str(session_id)

        position = getPosition()
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
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            global current_user, current_user_uid
            current_user = authe.sign_in_with_email_and_password(email, password)
            current_user_uid = current_user["localId"]
            session_id = current_user["idToken"]
            request.session["uid"] = str(session_id)

            position = getPosition()
            print(position)
            if position == "authority":
                print("hello")
                return HttpResponseRedirect(reverse("reports"))
            elif position == "pharmacist":
                return HttpResponseRedirect(reverse("medicines"))
            elif position == "user":
                return HttpResponseRedirect(reverse("appuser"))
            else:
                return HttpResponseRedirect(reverse("users"))
        except:
            messages.error(request, "Invalid Credentials")
            return render(request, "login.html")

    return render(request, "login.html", {"title": "login"})


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("login"))


#############################################
#                DASHBOARDS                 #
#############################################


def reportsDashboard(request):
    if getPosition() != None:
        if getPosition() == "authority":
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
    if getPosition() != None:
        if getPosition() == "pharmacist":
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
    return render(request, "appuser.html")


def notify(request, id):
    med_ref = db.collection(u"Medicines").document(id)
    med_ref.set({u"resolved": True}, merge=True)
    medicine = med_ref.get().to_dict().get("medicine")
    uId = med_ref.get().to_dict().get("uId")
    user = firebase_admin.auth.get_user(uId)
    print(user.email)
    send_mail(user.email, getPharmacyDetails(current_user_uid), medicine)
    return HttpResponseRedirect(reverse("medicines"))


def resolve(request, id):
    report_ref = db.collection(u"Reports").document(id)
    report_ref.set({u"resolved": True}, merge=True)
    return HttpResponseRedirect(reverse("reports"))


def page404(request):
    return render(request, "404.html")


def reportCondition(request):
    if request.method == "POST":
        address = request.POST.get(u"address")
        contact = request.POST.get(u"contact")
        age = request.POST.get(u"age")
        gender = request.POST.get(u"gender")
        case = request.POST.get(u"case")
        condition = request.POST.get(u"condition")
        treatment = request.POST.get(u"treatment")
        area = request.POST.get(u"area")
        info = request.POST.get(u"info")
        location = [
            float(request.POST.get(u"lat")),
            float(request.POST.get(u"lon")),
        ]
        uid = current_user_uid
        abc = db.collection(u"Reports").get()
        list_items = []
        for i in abc:
            list_items.append(i)
        count = len(list_items) + 1
        data = {
            u"area": area,
            u"address": address,
            u"contact": contact,
            u"age": age,
            u"gender": gender,
            u"case": case,
            u"condition": condition,
            u"treatment": treatment,
            u"uId": uid,
            u"location": location,
            u"description": info,
        }
        db.collection(u"Reports").document(str(count)).set(data)
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
        uid = current_user_uid
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

    return render(request, "ordermeds.html")
