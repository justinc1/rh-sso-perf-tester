#!/usr/bin/env python

import logging
import sys
import kcapi
from pytictoc import TicToc
import asyncio

log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(level=log_level)
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
    logger.info(f"User count: {users.count()}")
    uu1 = users.findFirst({"key":"username", "value": "user000001"})
    logger.info(f"User 01:: {uu1}")
    uu2 = users.search({"firstName": "remove-me"})
    logger.info(f"User 2:: {uu2}")


async def cleanup_users_async(users, nn):
    tasks1 = []
    loop = asyncio.get_event_loop()
    logger.info(f"Removing users with username user[000000..{nn:06}]")
    for ii in range(nn):
        username = f"user{ii:06}"
        tasks1.append(loop.run_in_executor(None, users.search, {"username": username}))
    user_ids = []
    for tt1 in tasks1:
        uu_list = await tt1
        logger.debug(f"Removing user {uu_list}")
        if uu_list:
            user_ids.append(uu_list[0]["id"])

    tasks2 = []
    for user_id in user_ids:
        logger.debug(f"Removing user id {user_id}")
        tasks2.append(loop.run_in_executor(None, users.remove, user_id))
    for tt2 in tasks2:
        await tt2


def cleanup_users(nn):
    loop = asyncio.get_event_loop()
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before cleanup: {users.count()}")
    timer.tic()
    loop.run_until_complete(cleanup_users_async(users, nn))
    timer.toc()
    logger.info(f"User count after cleanup: {users.count()}")


async def create_users(nn):
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before create: {users.count()}")
    timer.tic()
    tasks = []
    loop = asyncio.get_event_loop()
    for ii in range(nn):
        username = f"user{ii:06}"
        logger.debug(f"username: {username}")
        tasks.append(loop.run_in_executor(None, users.create, {"username":username}))
        # logger.info(f"User is_ok: {uu.isOk()}")
    # user_uuids = []
    for tt in tasks:
        uu = await tt
        logger.debug(f"uu.isOk={uu.isOk()} uu.response={uu.response}")
        # FFF response is empty
        # if uu.isOk():
        #     user_uuids.append(uu.response.json()["id"])
    timer.toc()
    logger.info(f"User count after create: {users.count()}")

def main():
    # test_ro()

    nn = int(sys.argv[4])
    loop = asyncio.get_event_loop()
    cleanup_users(nn)
    loop.run_until_complete(create_users(nn))
    cleanup_users(nn)


if __name__ == "__main__":
    main()
