#!/usr/bin/env python

import logging
import sys
import kcapi
from pytictoc import TicToc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

realm = "master"


def get_kc():
    api_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    oid_client = kcapi.OpenID({
        "client_id": "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password",
        "realm" : realm
    }, api_url)
    token = oid_client.getToken()
    # 'expires_in': 60,
    kc = kcapi.Keycloak(token, api_url)
    return kc


def test_ro():
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count: {len(users.all())}")
    uu1 = users.findFirst({"key":"username", "value": "user000001"})
    logger.info(f"User 01:: {uu1}")


def cleanup_users(nn=10):
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before cleanup: {len(users.all())}")
    timer.tic()
    for ii in range(nn):
        username = f"user{ii:06}"
        uu = users.findFirst({"key":"username", "value": username})
        users.remove(uu["id"])
        logger.info(f"User deleted: {uu}")
    timer.toc()
    logger.info(f"User count after cleanup: {len(users.all())}")


def create_users(nn=10):
    cleanup_users(nn)
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before: {len(users.all())}")
    timer.tic()
    for ii in range(nn):
        username = f"user{ii:06}"
        logger.info(f"username: {username}")
        uu = users.create({"username":username})
        logger.info(f"User is_ok: {uu.isOk()}")
    timer.toc()
    logger.info(f"User count after: {len(users.all())}")


def main():
    # test_ro()
    create_users()


if __name__ == "__main__":
    main()
