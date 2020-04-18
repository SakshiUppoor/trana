from django.shortcuts import render
import os
import firebase_admin
from firebase_admin import credentials, firestore

from django.contrib import messages
from django.contrib import auth
from firebase import firebase
import pyrebase

###########################
# FIRESTORE CONFIGURATION #
###########################

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "ServiceAccountKey.json")
)
deafult_app = firebase_admin.initialize_app(cred)

db = firestore.client()


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


def home(request):
    return render(request, "home.html")


def get_components():
    reports_ref = db.collection(u"Medicines")
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        co_list.append(
            [report.to_dict()["locationNew"][0], report.to_dict()["locationNew"][1]]
        )
        entry = {}
        for field in report.to_dict():
            if field != "locationNew":
                entry[field] = report.to_dict()[field]
        entry["id"] = len(reports_list)
        reports_list.append(entry)
    return co_list, reports_list


def reportsDashboard(request):
    co_list, reports_list = get_components()
    context = {
        "co_list": co_list,
        "reports": reports_list,
    }
    return render(request, "dashboard.html", context)


def signup(request):
    name = request.POST.get(u"username")
    email = request.POST.get(u"email")
    position = request.POST.get(u"position")
    password = request.POST.get(u"password1")

    firebase_admin.auth.create_user(email=email, password=password)

    data = {"name": name, "position": position}
    db.collection(u"authorities").document(u"details").set(data)

    return render(request, "signup.html")


def login_view(request):
    return render(request, "login.html")


def post_login(request):
    email = request.POST["email"]
    password = request.POST["password"]
    try:
        user = authe.sign_in_with_email_and_password(email, password)
    except:
        messages.error(request, "Invalid Credentials")
        return render(request, "login.html")
    print(user)
    session_id = user["idToken"]
    request.session["uid"] = str(session_id)
    return render(request, "postlogin.html", {"e": email})


def logout_view(request):
    auth.logout(request)
    return render(request, "login.html")
