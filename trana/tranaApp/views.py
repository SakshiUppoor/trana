from django.shortcuts import render

# Create your views here.
import pyrebase

config = {
  'apiKey': "AIzaSyDXMensLWaA5AvH2M7r6DhR6oCIu1kXG5U",
  'authDomain': "trana-cfbcf.firebaseapp.com",
  'databaseURL': "https://trana-cfbcf.firebaseio.com",
  'projectId': "trana-cfbcf",
  'storageBucket': "trana-cfbcf.appspot.com",
  'messagingSenderId': "105597355531",
  'appId': "1:105597355531:web:b7d7645d90867fb34a690e",
  'measurementId': "G-FQ9WQ7Z7VQ"
}

firebase = pyrebase.initialize_app(config)
auth=firebase.auth()

def home(request):
    return render(request,'home.html')

def login_view(request):
    return render(request,'login.html')

def post_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except:
        messages.error("Invalid Credentials")
        return render(request,'login.html')
    return render(request,'postlogin.html',{'e':email})