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
    user_ref = db.collection(u"Users").document(current_user_uid)
    user = user_ref.get()
    if user.exists:
        return user.to_dict().get("position")
    return None


def get_components(collection):
    reports_ref = db.collection(collection)
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        if report.to_dict().get("location"):
            co_list.append(
                [report.to_dict()["location"][0], report.to_dict()["location"][1]]
            )
        entry = {}
        entry["id"] = len(reports_list)
        for field in report.to_dict():
            entry[field] = report.to_dict()[field]
        reports_list.append(entry)
    return co_list, reports_list


#############################################
#       AUTHENTICATION & LOGIN STUFF        #
#############################################


def signup(request):
    if request.method == "POST":
        name = request.POST.get(u"username")
        email = request.POST.get(u"email")
        position = request.POST.get(u"position")
        password = request.POST.get(u"password1")

        user = firebase_admin.auth.create_user(email=email, password=password)
        uid = user.uid
        data = {u"name": name, u"position": position}
        db.collection(u"Users").document(uid).set(data)

    return render(request, "signup.html")


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
            else:
                return HttpResponseRedirect(reverse("users"))
        except:
            messages.error(request, "Invalid Credentials")
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    auth.logout(request)
    return render(request, "login.html")


#############################################
#                DASHBOARDS                 #
#############################################


def reportsDashboard(request):
    co_list, reports_list = get_components("Reports")
    context = {
        "co_list": co_list,
        "reports": reports_list,
    }
    return render(request, "reports.html", context)


def medicinesDashboard(request):
    co_list, medicines_list = get_components("Medicines")
    context = {
        "co_list": co_list,
        "medicines": medicines_list,
    }
    return render(request, "medicines.html", context)


def usersDashboard(request):

    return render(request, "users.html")


def notify(request, UId):
    user = firebase_admin.auth.get_user(UId)
    print(user.email)
    send_mail(user.email)
    return HttpResponseRedirect(reverse("medicines"))
