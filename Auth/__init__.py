import pyrebase

# Configuration
config = {
  "apiKey": "AIzaSyDvqkK0qG_Mhdh2AgMwZcWNUfIcsvpHZCU",
  "authDomain": "assignment2-21973.firebaseapp.com",
  "databaseURL": "https://assignment2-21973-default-rtdb.firebaseio.com",
  "projectId": "assignment2-21973",
  "storageBucket": "assignment2-21973.appspot.com",
  "messagingSenderId": "625821177645",
  "appId": "1:625821177645:web:ecf64eb22a9ea7a619e5a4",
  #"measurementId": ""
}

# Initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

request_user = {
  "is_logged_in": False,
  "name": "",
  "email": "",
  "uid": ""
}