from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from Auth import auth, db, request_user

app = Flask(__name__)


# Login
@app.route("/")
def login():
    if request_user["is_logged_in"]:
        return render_template("dashboard.html", email=request_user["email"], name=request_user["name"])
    else:
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    auth.current_user = None
    request_user["is_logged_in"] = False
    return render_template("login.html")


# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")


# Welcome page
@app.route("/dashboard")
def welcome():
    if request_user["is_logged_in"]:
        return render_template("dashboard.html", email=request_user["email"], name=request_user["name"])
    else:
        return redirect(url_for('login'))


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        result = request.form  # Get the data
        email = result["email"]
        password = result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)

            request_user["is_logged_in"] = True
            request_user["email"] = user["email"]
            request_user["uid"] = user["localId"]

            data = db.child("users").get()
            request_user["name"] = data.val()[request_user["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('dashboard'))
        except:
            # If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if request_user["is_logged_in"]:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)

            request_user["is_logged_in"] = True
            request_user["email"] = user["email"]
            request_user["uid"] = user["localId"]
            request_user["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(request_user["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for('dashboard'))
        except:
            # If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if request_user["is_logged_in"]:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('register'))


if __name__ == "__main__":
    app.run(debug=True)