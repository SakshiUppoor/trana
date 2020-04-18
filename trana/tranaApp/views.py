from django.shortcuts import render
from django.contrib import messages
from django.contrib import auth
from firebase import firebase
# Create your views here.
import pyrebase
import firebase_admin
from firebase_admin import credentials,firestore,auth
cred=credentials.Certificate('./ServiceAccountKey.json')
default_app=firebase_admin.initialize_app(cred)
db=firestore.client()

config = {
  'apiKey': "AIzaSyDXMensLWaA5AvH2M7r6DhR6oCIu1kXG5U",
  'authDomain': "trana-cfbcf.firebaseapp.com",
  'databaseURL': "https://trana-cfbcf.firebaseio.com",
  'projectId': "trana-cfbcf",
  'storageBucket': "trana-cfbcf.appspot.com",
  'messagingSenderId': "105597355531",
  'appId': "1:105597355531:web:b7d7645d90867fb34a690e",
  'measurementId': "G-FQ9WQ7Z7VQ",
 
}

firebase = pyrebase.initialize_app(config)
authe=firebase.auth()
#db = firebase.database()
#firebase = firebase.FirebaseApplication("https://trana-cfbcf.firebaseio.com", None)

def home(request):
    return render(request,'home.html')

def signup(request):
    name=request.POST.get(u'username')
    email=request.POST.get(u'email')
    position=request.POST.get(u'position')
    password=request.POST.get(u'password1')

    firebase_admin.auth.create_user(email=email,password=password)
    
    data={'name':name,'position':position}
    db.collection(u'authorities').document(u'details').set(data)
    
    
   
   
    return render(request,'signup.html')

def login_view(request):
    return render(request,'login.html')

def post_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        user = authe.sign_in_with_email_and_password(email, password)
    except:
        messages.error(request,"Invalid Credentials")
        return render(request,'login.html')
    print(user)
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request,'postlogin.html',{'e':email})

def logout_view(request):
    auth.logout(request)
    return render(request,'login.html')