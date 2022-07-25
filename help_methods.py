#!/usr/bin/env python

import kcapi


def get_kc(api_url, username, password):
    oid_client = kcapi.OpenID({
        "client_id": "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password",
        "realm": "master",
    }, api_url)
    token = oid_client.getToken()
    kc = kcapi.Keycloak(token, api_url)
    return kc


# def kc_build(kc, resource):
#     # args = parse_args()
#     kc = get_kc(args.url, args.username, args.password)
#     build = kc.build(resource, "master")
#     return build


def create_user(kc, username, data):
    # users = kc_build('users')
    users = kc.build("users", "master")
    old_users = users.search({"username": username})
    if old_users:
        print(f'FYI removing old user with username={username}')
        users.remove(old_users[0]['id'])

    # Create user without password
    user = users.create(data)
    return user


def assign_password(kc, username, password):
    users = kc.build("users", "master")
    user = users.search({"username": username})[0]
    user_credentials = {
        "temporary": False,
        "type": "password",
        "value": password,
    }
    user_info = {
        "key": "id",
        "value": user["id"],
    }
    users.updateCredentials(user_info, user_credentials)
    # Re-create users object to get new generated URLs
    users = kc.build("users", "master")
    return users


def create_group(kc, group_name):
    groups = kc.build("groups", "master")
    old_group = groups.findFirst({"key": "name", "value": group_name})
    if old_group:
        print(f'FYI removing old group with name={group_name}')
        groups.remove(old_group['id'])
    # Create group without roles
    group = groups.create({"name": group_name})
    return group


def assign_admin_roles_to_group(kc, group_name):
    roles = "default-roles-master"
    groups = kc.build("groups", "master")
    group_realm_roles = groups.realmRoles({"key": "name", "value": group_name})
    admin_group = group_realm_roles.add(["admin", roles])
    return admin_group


def assign_user_to_group(kc, username, group_name):
    users = kc.build("users", "master")
    # Assign members to existing group
    users.joinGroup({"key": "username", "value": username}, {"key": "name", "value": group_name})


def create_admin_user(kc, data, group_name, username):
    user = create_user(kc, username, data)
    assign_password(kc, data["username"], "testuserp")
    assign_user_to_group(kc, data["username"], group_name)
    return user
