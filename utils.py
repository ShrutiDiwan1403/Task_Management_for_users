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


def get_entities(entity_kind):
    query = client.query(kind=entity_kind)
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    return list(filter(None, data))

