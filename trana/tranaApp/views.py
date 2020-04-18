from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

from django.contrib import messages

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


def getPosition(uid):
    user_ref = db.collection(u"Users").document(uid)
    user = user_ref.get()
    if user.exists:
        return user.to_dict().get("position")
    return None


def get_components():
    reports_ref = db.collection(u"Reports")
    reports = reports_ref.stream()
    co_list = []
    reports_list = []
    for report in reports:
        co_list.append(
            [report.to_dict()["location"][0], report.to_dict()["location"][1]]
        )
        entry = {}
        for field in report.to_dict():
            if field != "location":
                entry[field] = report.to_dict()[field]
        entry["id"] = len(reports_list)
        reports_list.append(entry)
    return co_list, reports_list

def get_medicines():
    med_ref = db.collection(u"Medicines")
    medicines = med_ref.stream()
    co_list = []
    medicines_list = []
    for medicine in medicines:
        co_list.append(
            [medicine.to_dict()["locationNew"][0], medicine.to_dict()["locationNew"][1]]
        )
        entry = {}
        for field in medicine.to_dict():
            if field != "locationNew":
                entry[field] = medicine.to_dict()[field]
        entry["id"] = len(medicines_list)
        medicines_list.append(entry)
    return co_list, medicines_list


def reportsDashboard(request):
    co_list, reports_list = get_components()
    context = {
        "co_list": co_list,
        "reports": reports_list,
    }
    return render(request, "reports.html", context)


def medicinesDashboard(request):
    co_list, medicines_list = get_medicines()
    context = {
        "co_list": co_list,
        "medicines": medicines_list,
    }
    return render(request, "medicines.html", context)


def signup(request):
    if request.method == "POST":
        name = request.POST.get(u"username")
        email = request.POST.get(u"email")
        position = request.POST.get(u"position")
        password = request.POST.get(u"password1")

        user = firebase_admin.auth.create_user(email=email, password=password)
        uid = user.uid
        # print(firebase_admin.auth.UserInfo)
        data = {u"name": name, u"position": position}
        db.collection(u"Users").document(uid).set(data)

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = authe.sign_in_with_email_and_password(email, password)
        except:
            messages.error(request, "Invalid Credentials")
            return render(request, "login.html")
        uid = user["localId"]
        print(uid)
        session_id = user["idToken"]
        request.session["uid"] = str(session_id)

        position = getPosition(uid)
        print(position)
        if position == "authority":
            print("hello")
            return HttpResponseRedirect(reverse("reports"))
        elif position == "pharmacist":
            return HttpResponseRedirect(reverse("medicines"))
        else:
            return HttpResponseRedirect(reverse("users"))

    return render(request, "login.html")


def usersDashboard(request):
    return render(request, "users.html")


def logout_view(request):
    auth.logout(request)
    return render(request, "login.html")
