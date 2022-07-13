#!/usr/bin/env python

import argparse
import sys

import kcapi
import time


def parse_args():
    parser = argparse.ArgumentParser(description='Retrieve args')
    parser.add_argument('--url', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--iter', type=int, required=True )
    # TODO delay
    args = parser.parse_args()
    return args


def get_kc():
    args = parse_args()
    api_url = args.url
    username = args.username
    password = args.password

    oid_client = kcapi.OpenID({
        "client_id": "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password",
        "realm" : "master"
    }, api_url)
    token = oid_client.getToken()
    kc = kcapi.Keycloak(token, api_url)
    return kc


def kc_build(resource):
    kc = get_kc()
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
    testuser = {
        "enabled": 'true',
        "attributes": {},
        "username": username,
        "firstName": "test",
        "lastName": "user",
        "emailVerified": ""
    }
    users = kc_build('users')
    old_users = users.search({"username": username})
    if old_users:
        print(f'FYI removing old user with username={username}')
        users.remove(old_users[0]['id'])
    user = users.create(testuser)
    return user


def main():
    user = create_user()
    state = user.isOk()
    print('Status of creation:', state)

    args = parse_args()
    iter = args.iter
    count = 0
    while count < iter:
        count = count + 1

        users = kc_build('users')
        start = time.time()
        specific_user = users.search({"firstName": "test"})
        user_id = specific_user[0]['id']
        print(user_id)
        end = time.time()
        print('Time of cycle', [count], 'is', end - start)
        time.sleep(10)


if __name__ == "__main__":
    main()
