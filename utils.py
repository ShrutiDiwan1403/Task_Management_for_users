from DB import client
from Auth import db, request_user


def get_users_list():
    all_users = db.child("users").get()

    users_list = []
    for user in all_users.each():
        if request_user.get('uid') != user.item[0]:
            users_list.append({
                "user_id": user.item[0],
                "name": user.item[1].get("name", "")
            })

    return users_list


def get_all_entities(entity_type, board_id=None):
    query = client.query()
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    final_data = list()
    for obj in data:
        if obj.get("assigned_to") == request_user.get('uid'):
            if entity_type == "board":
                for obj2 in data:
                    if obj2.get("board_id") == obj.get("board_id") and obj2.get("board_name"):
                        final_data.append(obj2)
                    else:
                        continue
            elif entity_type == "task":
                for obj2 in data:
                    if obj2.get("board_id") == board_id and obj2.get("board_name", None) == None and \
                            obj2.get("assigned_to") == request_user.get('uid'):
                        final_data.append(obj2)
                    else:
                        continue
            else:
                continue
        else:
            continue

    return final_data


def get_entities(entity_kind, entity_type):
    query = client.query(kind=entity_kind)
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    if entity_type == "board":
        assigned_list = get_all_entities(entity_type)
    else:
        for obj in data:
            if obj.get("assigned_to") == request_user["uid"] or obj.get("owner_id") == request_user["uid"]:
                continue
            else:
                data.remove(obj)
        assigned_list = get_all_entities(entity_type, entity_type)

    data.extend(assigned_list)

    return list(filter(None, data))


def get_task_details(board_id, task_id):
    data = get_entities(board_id, "task")

    for obj in data:
        if obj.get("task_id") == task_id:
            return obj


def get_user_details(user_id):
    data = get_users_list()
    for obj in data:
        if obj.get("user_id") == user_id:
            return obj
    return {"name": request_user['name']}    
