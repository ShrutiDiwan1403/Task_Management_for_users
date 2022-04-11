import pyrebase

# Configuration
config = {
  "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "projectId": "",
  "storageBucket": "",
  "messagingSenderId": "",
  "appId": "",
  "measurementId": ""
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