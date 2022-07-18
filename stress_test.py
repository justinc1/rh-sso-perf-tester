#!/usr/bin/env python

import argparse
import logging
import time
import kcapi
from pytictoc import TicToc
import asyncio
from concurrent.futures import ProcessPoolExecutor, as_completed

log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

realm = "master"
firstName = "remove-me"


def user_generator(id0, id1):
    lastName = f"remove-me-{id0:02}"
    username = f"user-{id0:02}-{id1:06}"
    data = {
        "username": username,
        "firstName": firstName,
        "lastName": lastName,
    }
    return data

def parse_args():

    parser = argparse.ArgumentParser(description='Retrieve args')
    parser.add_argument('--url', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--requests', type=int, required=True)
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


async def cleanup_users_async(users):
    loop = asyncio.get_event_loop()
    logger.info(f"Removing users with firstName={firstName}]")
    user_ids = []
    first = 0
    page_size = 1000
    while True:
        uu_list = users.search({
            "firstName": firstName,
            "first": first,
            "max": page_size,
        })
        logger.info(f"Removing users count={len(uu_list)} first={first} page_size={page_size}")
        if uu_list:
            user_ids.extend([uu["id"] for uu in uu_list])
            first += page_size
        else:
            break

    tasks2 = []
    for user_id in user_ids:
        logger.debug(f"Removing user id {user_id}")
        tasks2.append(loop.run_in_executor(None, users.remove, user_id))
    for tt2 in tasks2:
        await tt2


def cleanup_users():
    loop = asyncio.get_event_loop()
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before cleanup: {users.count()}")
    timer.tic()
    loop.run_until_complete(cleanup_users_async(users))
    timer.toc()
    logger.info(f"User count after cleanup: {users.count()}")


async def create_users(id0, id1_max):
    timer = TicToc()
    kc =  get_kc()
    users = kc.build("users", realm)
    logger.info(f"User count before create: {users.count()}")
    timer.tic()
    tasks = []
    loop = asyncio.get_event_loop()
    debug_delay = 0.0  # 5.0
    for id1 in range(id1_max):
        data = user_generator(id0, id1)
        tasks.append(loop.run_in_executor(None, users.create, data))
        if debug_delay:
            logger.info(f"Creating user: username={data['username']}")
            time.sleep(debug_delay)
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
    return f"TTRT {id0:02} {id1_max} - users.count()={users.count()}"


def create_users_group(id0, id1_max):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(create_users(id0, id1_max))
    return result


def main():
    args = parse_args()
    id0_max = int(args.workers)
    id1_max = int(args.requests)

    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(cleanup_users)
        as_completed(future)

    future_to_id0 = dict()
    with ProcessPoolExecutor(max_workers=id0_max) as executor:
        for id0 in range(id0_max):
            future = executor.submit(create_users_group, id0, id1_max)
            future_to_id0[future] = id0

        for future in as_completed(future_to_id0):
            id0 = future_to_id0[future]
            worker_result = future.result()
            print(f"id0={id0:02} worker_result={worker_result}")

    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(cleanup_users)
        as_completed(future)


if __name__ == "__main__":
    main()
