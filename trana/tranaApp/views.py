from django.shortcuts import render

import os
import firebase_admin
<<<<<<< HEAD
from firebase_admin import credentials, firestore, auth
=======
from firebase_admin import credentials, firestore,auth
>>>>>>> a58b632dc6ee6c618574569c139b3f524c15bffc

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


def goToDashboard(uid):
    user_ref = db.collection(u"Users").document(u"1c1FsGUvCeTyqT5C5oxKbwVRpPl1")
    user = user_ref.get()
    if user.exists:
        print(u"Document data: {}".format(user.to_dict()))
    else:
        print(u"No such document!")


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
    return render(request, "reports.html", context)


def signup(request):
    if request.method=='POST':
        name=request.POST.get(u'username')
        email=request.POST.get(u'email')
        position=request.POST.get(u'position')
        password=request.POST.get(u'password1')

        user=firebase_admin.auth.create_user(email=email,password=password)
        uid=user.uid
        #print(firebase_admin.auth.UserInfo)
        data={u'name':name,u'position':position}
        db.collection(u'Users').document(uid).set(data)
    
    
   
   
    return render(request,'signup.html')

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
        goToDashboard(uid)
        # return HttpResponseRedirect(reverse("home"))
    return render(request, "login.html")


def post_login(request):

    return render(request, "postlogin.html")


def logout_view(request):
    auth.logout(request)
    return render(request, "login.html")
