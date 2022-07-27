#!/usr/bin/env python

import argparse
import kcapi
import time
import logging
from help_methods import make_user, create_group, assign_admin_roles_to_group, remove_group, remove_user, get_kc

log_level = logging.DEBUG
log_level = logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

test_realm = "stress-test"
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
    sso_group = parser.add_argument_group('sso')
    sso_group.add_argument('--url', required=True)
    sso_group.add_argument('--username', required=True)
    sso_group.add_argument('--password', required=True)

    subcommands = parser.add_subparsers(help='Subcommands', dest='command')
    cmd_prepare = subcommands.add_parser('prepare', help='Prepare before test')
    cmd_cleanup = subcommands.add_parser('cleanup', help='Cleanup after test')
    cmd_test = subcommands.add_parser('test', help='Run test')
    cmd_test.add_argument('--iter', type=int, required=True)
    cmd_test.add_argument('--period', type=int, default=10)
    cmd_test.add_argument('--action', type=str, choices=["query", "login"], default="login")

    args = parser.parse_args()
    return args


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
    def __init__(self, kc):
        # kc = get_kc(self._url, self._username, self._password)  # TODO realm needed?
        self._users = kc.build("users", test_realm)

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
        kc = get_kc(self._url, self._username, self._password, test_realm)
        users = kc.build("users", test_realm)

        # The test users cannot search
        # specific_user = users.search({"username": self._username})
        # Instead of search, just check token string is not empty.
        # TODO try to access "/auth/realms/stress-test/account/" URL to get info about currently logged in user
        token_str = kc.token.get_token()
        logger.debug(f"Username={self._username} got token={token_str}")
        assert (100 < len(token_str))


def cmd_prepare(kc):
    # create needed group and user
    # group = create_group(kc, "test-admins")
    # assign_admin_roles_to_group(kc, group_name)
    # print('Status of admin group creation:', group.isOk())

    data = user_data()
    user = make_user(kc, data, group_name, test_realm)
    print('Status of user creation:', user.isOk())


def cmd_test(kc, action_name, iterations, period):
    # run the test
    if action_name == "query":
        action = QueryUserAction(kc)
    elif action_name == "login":
        action = LoginUserAction("testuser", "testuserp")
    else:
        raise NotImplementedError(f"Unsupported action={action_name}")

    count = 0
    while count < iterations:
        action.run_once(count)
        count += 1
        time.sleep(period)


def cmd_cleanup(kc):
    # remove test user and group
    # remove_group(kc, "test-admins")
    remove_user(kc, "testuser", test_realm)


def main():
    args = parse_args()
    kc = get_kc(args.url, args.username, args.password)
    if args.command == 'prepare':
        cmd_prepare(kc)
    elif args.command == 'test':
        cmd_test(kc, args.action, args.iter, args.period)
    elif args.command == 'cleanup':
        cmd_cleanup(kc)
    else:
        raise NotImplementedError(f"Subcommand unknown: {args.command}")


if __name__ == "__main__":
    main()
