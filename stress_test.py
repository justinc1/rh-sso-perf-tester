#!/usr/bin/env python

import argparse
import logging
import time
import kcapi
from pytictoc import TicToc
import asyncio
from concurrent.futures import ProcessPoolExecutor, as_completed
from help_methods import make_user, create_group, assign_admin_roles_to_group, get_kc

#log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

realm = "stress-test"
firstName = "remove-me"
group_name = "test-admins"


class KcConnectParams:
    # Params needed to connect to Keycloak API
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password


def user_generator(worker_num, user_num):
    lastName = f"remove-me-{worker_num:02}"
    username = f"user-{worker_num:02}-{user_num:06}"
    data = {
        "enabled": 'true',
        "attributes": {},
        "username": username,
        "firstName": firstName,
        "lastName": lastName,
        "emailVerified": "",
    }
    return data


def parse_args():
    def add_workers_period_arg(subcmd):
        subcmd.add_argument('--workers', type=int, required=True,
                                 help="How many worker processes to start")
        subcmd.add_argument('--users', type=int, required=True,
                                 help="How many users should each worker create")
        subcmd.add_argument('--period', type=float, default=0.0,
                              help="Optionally delay to wait between requests")

    parser = argparse.ArgumentParser(description='Stress load for RedHat SSO')
    sso_group = parser.add_argument_group('sso')
    sso_group.add_argument('--url', required=True,
                           help="API URL")
    sso_group.add_argument('--username', required=True,
                           help="Admin user username. Administrator rights are required.")
    sso_group.add_argument('--password', required=True,
                           help="Admin user password")

    subcommands = parser.add_subparsers(help='Subcommands', dest='command')
    cmd_prepare = subcommands.add_parser('prepare', help='Prepare before test')
    add_workers_period_arg(cmd_prepare)
    cmd_cleanup = subcommands.add_parser('cleanup', help='Cleanup after test')
    cmd_test = subcommands.add_parser('test', help='Run test')
    add_workers_period_arg(cmd_test)

    args = parser.parse_args()
    return args


async def cleanup_users_async(users):
    loop = asyncio.get_event_loop()
    logger.info(f"Removing users with firstName={firstName}]")
    user_ids = []
    first = 0
    page_size = 1000
    timer = TicToc()
    timer.tic()
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
    timer.toc("Cleanup users part 1 - search for UUIDs duration: ")

    timer.tic()
    tasks2 = []
    for user_id in user_ids:
        logger.debug(f"Removing user id {user_id}")
        tasks2.append(loop.run_in_executor(None, users.remove, user_id))
    for tt2 in tasks2:
        await tt2
    timer.toc("Cleanup users part 2 - removing users duration: ")


def cleanup_users(kc):
    loop = asyncio.get_event_loop()
    timer = TicToc()
    users = kc.build("users", realm)
    logger.info('=================================== test cleanup => realm: '+ realm)
    logger.info(f"User count before cleanup: {users.count()}")
    timer.tic()
    loop.run_until_complete(cleanup_users_async(users))
    timer.toc()
    logger.info(f"User count after cleanup: {users.count()}")


async def create_users(kc, worker_num, users_count, period):
    timer = TicToc()
    users = kc.build("users", realm)
    logger.info(f"User count before create: {users.count()}")
    timer.tic()
    tasks = []
    loop = asyncio.get_event_loop()
    for user_num in range(users_count):
        data = user_generator(worker_num, user_num)
        # tasks.append(loop.run_in_executor(None, users.create, data))
        tasks.append(loop.run_in_executor(None, make_user, kc, data, group_name, realm))
        if period:
            logger.debug(f"Creating user: username={data['username']}")
            time.sleep(period)
        # logger.info(f"User is_ok: {uu.isOk()}")
    # user_uuids = []
    for tt in tasks:
        uu = await tt
        logger.debug(f"uu.isOk={uu.isOk()} uu.response={uu.response}")
        # FFF response is empty
        # if uu.isOk():
        #     user_uuids.append(uu.response.json()["id"])
    timer.toc(f"Worker {worker_num:02} created {users_count} users in")
    logger.info(f"User count after create: {users.count()}")
    return f"TTRT {worker_num:02} {users_count} - users.count()={users.count()}"


def create_users_group(kcparams, worker_num, users_count, period):
    kc = get_kc(kcparams.url, kcparams.username, kcparams.password)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(create_users(kc, worker_num, users_count, period))
    return result


def users_get_token_wrapper(kcparams, worker_num, users_count, period):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(users_get_token(kcparams, worker_num, users_count, period))
    return result


async def users_get_token(kcparams, worker_num, users_count, period):
    timer = TicToc()
    timer.tic()
    tasks = []
    loop = asyncio.get_event_loop()
    for user_num in range(users_count):
        data = user_generator(worker_num, user_num)
        tasks.append(loop.run_in_executor(None, user_get_token, kcparams, data, realm))
        if period:
            logger.debug(f"Logging in as user: username={data['username']}")
            time.sleep(period)
    for tt in tasks:
        token_str = await tt
        # logger.debug(f"login as user - uu={uu}")
    timer.toc(f"Worker {worker_num:02} logged-in {users_count} users in")
    return f"TTRT login as user - {worker_num:02} {users_count}"


def user_get_token(kcparams, user_data, realm):
    kc = get_kc(kcparams.url, user_data["username"], "testuserp", realm)
    token_str = kc.token.get_token()
    logger.debug(f"Username={user_data['username']}  token={token_str}")
    assert (100 < len(token_str))
    return token_str


def cmd_prepare(kcparams, workers_count, users_count, period):
    # kc = get_kc(kcparams.url, kcparams.username, kcparams.password)
    # create_group(kc, group_name)
    # assign_admin_roles_to_group(kc, group_name)
    # Ugly - make sure existing socket is NOT reused by worker processes.
    # Or, create also group in a worker process.
    # kc = None
    # import kcapi
    # kcapi.rest.crud.KeycloakCRUD._global_default_session = None

    future_to_worker_num = dict()
    with ProcessPoolExecutor(max_workers=workers_count) as executor:
        for worker_num in range(workers_count):
            # each worker process needs its own socket to Keycloak
            future = executor.submit(create_users_group, kcparams, worker_num, users_count, period)
            future_to_worker_num[future] = worker_num

        for future in as_completed(future_to_worker_num):
            worker_num = future_to_worker_num[future]
            worker_result = future.result()
            print(f"worker_num={worker_num:02} worker_result={worker_result}")


def cmd_test(kcparams, workers_count, users_count, period):
    future_to_worker_num = dict()
    with ProcessPoolExecutor(max_workers=workers_count) as executor:
        for worker_num in range(workers_count):
            # each worker process needs its own socket to Keycloak
            future = executor.submit(users_get_token_wrapper, kcparams, worker_num, users_count, period)
            future_to_worker_num[future] = worker_num

        for future in as_completed(future_to_worker_num):
            worker_num = future_to_worker_num[future]
            worker_result = future.result()
            print(f"worker_num={worker_num:02} worker_result={worker_result}")


def cmd_cleanup(kcparams):
    kc = get_kc(kcparams.url, kcparams.username, kcparams.password)
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(cleanup_users, kc)
        as_completed(future)


def main():
    args = parse_args()
    kcparams = KcConnectParams(args.url, args.username, args.password)
    if args.command == 'prepare':
        cmd_prepare(kcparams, args.workers, args.users, args.period)  # TODO args.users, not args.requests
    elif args.command == 'test':
        cmd_test(kcparams, args.workers, args.users, args.period)
    elif args.command == 'cleanup':
        cmd_cleanup(kcparams)
    else:
        raise NotImplementedError(f"Subcommand unknown: {args.command}")


if __name__ == "__main__":
    main()
