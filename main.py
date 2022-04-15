import uuid
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

from utils import get_users_list, get_entities, get_task_details, get_user_details
from DB import client, datastore
from Auth import auth, db, request_user

app = Flask(__name__)


# Login
@app.route("/")
def login():
    if request_user["is_logged_in"] == True:
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
def dashboard():
    if request_user["is_logged_in"]:
        data = get_entities(request_user["uid"], "board")
        return render_template("dashboard.html", data=data, user_id=request_user["uid"], email=request_user["email"],
                               name=request_user["name"])
    else:
        return redirect(url_for('login'))


@app.route("/list")
def task_display_list():
    if request_user["is_logged_in"]:
        return render_template("list.html", email=request_user["email"], name=request_user["name"])
    else:
        return redirect(url_for('login'))


@app.route("/task-detail")
def task_details():
    if request_user["is_logged_in"]:
        return render_template("task-details.html", email=request_user["email"], name=request_user["name"])
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
            global request_user
            request_user["is_logged_in"] = True
            request_user["email"] = user["email"]
            request_user["uid"] = user["localId"]

            data = db.child("users").get()
            request_user["name"] = data.val()[request_user["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('dashboard'))
        except Exception as e:
            # If there is any error, redirect back to login
            print(e)
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

            # Create User entity in datastore
            key = client.key(request_user["uid"], request_user["name"])
            entity = datastore.Entity(key=key)
            client.put(entity)

            # Go to welcome page
            return redirect(url_for('login'))
        except:
            # If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        return redirect(url_for('login'))


@app.route("/create-board", methods=["POST", "GET"])
def create_board():
    if request_user["is_logged_in"]:
        if request.method == "POST":  # Only listen to POST
            result = request.form
            board_id = str(uuid.uuid4())
            board_name = result.get("board_name", None)
            if board_name.strip() != "":
                # Adding board in user entity
                key = client.key(request_user["uid"], board_id)
                entity = datastore.Entity(key=key)
                entity.update({
                    "board_id": board_id,
                    "board_name": board_name,
                    "owner_id": request_user["uid"]
                })
                client.put(entity)

                # Creating board entity
                key_2 = client.key(board_id, board_name)
                entity_2 = datastore.Entity(key=key_2)
                client.put(entity_2)
                return redirect(url_for('dashboard'))
            else:
                return render_template("create_board.html")
        elif request.method == "GET":
            return render_template("create_board.html")

    else:
        return render_template("login.html")


@app.route("/update-board/<board_id>", methods=["POST"])
def update_board(board_id):
    if request_user["is_logged_in"]:
        if request.method == "POST":  # Only listen to POST
            result = request.form
            board_name = result.get("board_name", None)

            # Adding board in user entity
            key = client.key(request_user["uid"], board_id)
            entity = datastore.Entity(key=key)
            entity.update({
                "board_name": board_name
            })
            client.put(entity)

            # Creating board entity
            key_2 = client.key(board_id, board_name)
            entity_2 = datastore.Entity(key=key_2)
            client.put(entity_2)
    else:
        return render_template("login.html")


@app.route("/<user_id>/<board_id>/create-task", methods=["POST", "GET"])
def create_task(user_id, board_id):
    if request_user["is_logged_in"]:
        if request.method == "POST":  # Only listen to POST
            result = request.form
            task_id = str(uuid.uuid4())
            task_name = result.get("task_name", None)
            due_date = result.get("due_date", None)
            completed = result.get("completed", False)
            assigned_to = result.get("assigned_to", None)
            if task_name.strip() != "" and assigned_to != None:
                # Adding task in board entity
                key = client.key(str(board_id), task_id)
                entity = datastore.Entity(key=key)
                entity.update({
                    "task_id": task_id,
                    "task_name": task_name,
                    "due_date": due_date,
                    "completed": completed,
                    "assigned_to": assigned_to,
                    "owner_id": user_id,
                    "board_id": board_id
                })
                client.put(entity)
                return redirect(url_for('.list_tasks', owner_id=user_id, board_id=board_id, user_id=request_user['uid']))
            else:
                return render_template("create_task.html", user_id=request_user['uid'], board_id=board_id,
                                       users_list=get_users_list())
        elif request.method == "GET":
            return render_template("create_task.html", user_id=request_user['uid'], board_id=board_id,
                                   users_list=get_users_list())
    else:
        return render_template("login.html")


@app.route("/<board_id>/update-task/<task_id>", methods=["POST", "GET"])
def update_task(board_id, task_id):
    if request_user["is_logged_in"]:
        if request.method == "POST":  # Only listen to POST
            result = request.form
            task_name = result.get("task_name", None)
            due_date = result.get("due_date", None)
            completed = result.get("completed", False)
            assigned_to = result.get("assigned_to", None)
            user_id = result.get("owner_id", None)

            # Updating task in board entity
            key = client.key(board_id, task_id)
            entity = datastore.Entity(key=key)
            entity.update({
                "task_id": task_id,
                "task_name": task_name,
                "due_date": due_date,
                "assigned_to": assigned_to,
                "completed": completed,
                "owner_id": user_id,
                "board_id": board_id
            })
            client.put(entity)
            return redirect(url_for('.list_tasks', user_id=request_user['uid'], board_id=board_id, owner_id=user_id,))
        elif request.method == "GET":
            data = get_task_details(board_id, task_id)

            return render_template("edit_task.html", users_list=get_users_list(), data=data, task_id=task_id,
                                   board_id=board_id)
    else:
        return render_template("login.html")


@app.route("/<owner_id>/<board_id>/list-tasks", methods=["GET"])
def list_tasks(owner_id, board_id):
    if request_user["is_logged_in"]:
        data = get_entities(board_id, "task")
        return render_template("list.html", user_id=request_user['uid'], owner_id=owner_id, board_id=board_id, data=data)
    else:
        return redirect(url_for('login'))


@app.route("/<board_id>/view-task/<task_id>", methods=["GET"])
def task_datils(board_id, task_id):
    if request_user["is_logged_in"]:
        data = get_task_details(board_id, task_id)
        user_id = data['assigned_to']
        user = get_user_details(user_id)
        return render_template("task-details.html", data=data, user=user, board_id=board_id)
    else:
        return redirect(url_for('login'))


@app.route("/<board_id>/delete-board/<board_name>", methods=["GET"])
def delete_board(board_id, board_name):
    # Adding board in user entity
    key = client.key(request_user["uid"], board_id)
    entity = datastore.Entity(key=key)
    client.put(entity)

    # Creating board entity
    key_2 = client.key(board_id, board_name)
    client.delete(key_2)
    return redirect(url_for('dashboard'))


@app.route("/<owner_id>/<board_id>/delete-task/<task_id>", methods=["GET"])
def delete_task(owner_id, board_id, task_id):
    key = client.key(str(board_id), task_id)
    entity = datastore.Entity(key=key)
    client.put(entity)
    return redirect(url_for('.list_tasks', user_id=request_user['uid'], board_id=board_id, owner_id=owner_id))

if __name__ == "__main__":
    app.run(debug=True)