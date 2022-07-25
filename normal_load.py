#!/usr/bin/env python

import argparse
import kcapi
import time
import logging
from help_methods import create_admin_user, create_group, assign_admin_roles_to_group

log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

group_name = "test-admins"


def user_data():
    username = "testuser"
    data = {
        "enabled": 'true',
        "attributes": {},
        "username": username,
        "firstName": "test",
        "lastName": "user",
        "emailVerified": "",
    }
    return data


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
    data = user_data()
    args = parse_args()
    kc = get_kc(args.url, args.username, args.password)
    group = create_group(kc, "test-admins")
    assign_admin_roles_to_group(kc, group_name)
    user = create_admin_user(kc, data, group_name, data['username'])
    state1 = user.isOk()
    state2 = group.isOk()
    print('Status of admin group creation:', state2, ',', 'Status of user creation:', state1)

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
