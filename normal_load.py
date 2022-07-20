#!/usr/bin/env python

import argparse
import sys
import kcapi
import time
import logging

log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Retrieve args')
    parser.add_argument('--url', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--iter', type=int, required=True)
    parser.add_argument('--period', type=int, default=10)
    parser.add_argument('--action', type=str, choices=["query", "login"], default="login")
    args = parser.parse_args()
    return args


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


def kc_build(resource):
    args = parse_args()
    kc = get_kc(args.url, args.username, args.password)
    build = kc.build(resource, "master")
    return build


def get_userinfo(name):
    users = kc_build('users')
    # specific_user = users.search({"firstName": "test"})
    specific_user = users.search({"firstName": name})
    return specific_user


def create_group():
    groups = kc_build('groups')
    group = groups.create({"name": "master"})
    return group


def create_user():
    username = "testuser"
    password = "testuserp"
    group_name = "test-admins"

    testuser = {
        "enabled": 'true',
        "attributes": {},
        "username": username,
        "firstName": "test",
        "lastName": "user",
        "emailVerified": "",
    }
    users = kc_build('users')
    old_users = users.search({"username": username})
    if old_users:
        print(f'FYI removing old user with username={username}')
        users.remove(old_users[0]['id'])
    response = users.create(testuser)

    user = users.search({"username": username})[0]
    user_credentials = {
        "type": "password",
        "temporary": False,
        "value": password,
    }
    user_info = {
        "key": "id",
        "value": user["id"],
    }
    # works only if we have less than 100 users...
    state = users.updateCredentials(user_info, user_credentials).isOk()
    # users.updateCredentials - it adds "/reset-password" to generated URLs,
    # so we need to re-create users object.
    users = kc_build('users')
    # resp2 = users.reset_password(user['id'], password, temporary=False)

    # make user an admin: add test-admins group
    groups = kc_build("groups")
    old_group = groups.findFirst({"key": "name", "value": group_name})
    if old_group:
        print(f'FYI removing old group with name={group_name}')
        groups.remove(old_group['id'])
    groups.create({"name": "test-admins"}).isOk()
    # make user an admin: add testuser to test-admins group
    users.joinGroup({"key": "username", "value": username}, {"key": "name", "value": group_name}).isOk()
    # make user an admin: add realmRole admin to test-admins group
    group_realm_roles = groups.realmRoles({"key": "name", "value": group_name})
    group_realm_roles.add(["admin", "default-roles-master"])

    # test: login as testuser
    args = parse_args()
    kc2 = get_kc(args.url, username, password)
    users2 = kc2.build("users", "master")
    self_user_info = users2.search({"username": username})
    print(f"Evaluate as {username}: user uuid={self_user_info[0]['id']} users2.count()={users2.count()}")

    return response


class Action:
    def run_once(self, count):
        start = time.time()
        self._run_once_body(count)
        end = time.time()
        duration = end - start
        print(f'action={type(self).__name__} iteration={count} duration={duration}')


class QueryUserAction(Action):
    def __init__(self):
        self._users = kc_build('users')

    def _run_once_body(self, count):
        specific_user = self._users.search({"username": "testuser"})
        user_id = specific_user[0]['id']
        logger.debug(f"user_id={user_id}")


class LoginUserAction(Action):
    def __init__(self, username, password):
        args = parse_args()
        self._url = args.url
        self._username = username
        self._password = password

    def _run_once_body(self, count):
        kc = get_kc(self._url, self._username, self._password)
        users = kc.build("users", "master")
        # self._users = users2

        specific_user = users.search({"username": self._username})
        user_id = specific_user[0]['id']
        logger.debug(f"user_id={user_id}")


def main():
    user = create_user()
    state = user.isOk()
    print('Status of creation:', state)

    args = parse_args()
    iter = args.iter
    count = 0

    if args.action == "query":
        action = QueryUserAction()
    elif args.action == "login":
        action = LoginUserAction("testuser", "testuserp")
    else:
        raise NotImplementedError(f"Unsupported action={args.action}")

    while count < iter:
        action.run_once(count)
        count += 1
        time.sleep(args.period)


if __name__ == "__main__":
    main()
