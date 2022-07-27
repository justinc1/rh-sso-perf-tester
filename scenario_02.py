#!/usr/bin/env python

import os
import time
import sys
import logging
from datetime import datetime
from scenario import ExtCommand, Task, Stage, Scenario

LOGGING_LEVEL = logging.DEBUG
# LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(process)d %(message)s'
logging.basicConfig(
    level=LOGGING_LEVEL,
    format=LOGGING_FORMAT,
)
logger = logging.getLogger(__name__)


def main():
    sso_url_user_pass = "--url $APIURL --username $SSO_API_USERNAME --password $SSO_API_PASSWORD"
    cmd_normal_load_base = f"./normal_load.py {sso_url_user_pass}"
    cmd_stress_load_base = f"./stress_test.py {sso_url_user_pass}"

    cmd_normal_load_test = " --action login"
    cmd_stress_load_test = " --workers 2"
    if 0:
        cmd_normal_load_test += " --iter 12 --period 5"
        cmd_stress_load_test += " --users 1000"
    else:
        cmd_normal_load_test += " --iter 3 --period 1"
        cmd_stress_load_test += " --users 3 --period 1"

    # /ssh_command.py --hostname localhost --username uu3 --pkey $HOME/.ssh/id_rsa2 --sudo_password uu3p --command systemctl status crond
    cmd_ssh_base = f"./ssh_command.py"
    cmd_ssh_restart_cron = cmd_ssh_base + " --hostname localhost --command systemctl restart crond"

    scenario = Scenario(
        "sc02", stages=[
            Stage("cleanup-before", 0, [
                Task("all", 0, [
                    ExtCommand((cmd_normal_load_base + " cleanup").split()),
                    ExtCommand((cmd_stress_load_base + " cleanup").split()),
                    ]),
                ]),
            Stage("prepare", 1, [
                Task("all", 0, [
                    ExtCommand((cmd_normal_load_base + " prepare").split()),
                    ExtCommand((cmd_stress_load_base + " prepare" + cmd_stress_load_test).split()),
                    ]),
                ]),
            Stage("test", 2, [
                Task("normal_load", 0, [
                    ExtCommand("sleep 1".split()),
                    ExtCommand((cmd_normal_load_base + " test" + cmd_normal_load_test).split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                Task("stress_load", 1, [
                    ExtCommand("sleep 1".split()),
                    ExtCommand((cmd_stress_load_base + " test" + cmd_stress_load_test).split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                Task("restart_crond", 2, [
                    ExtCommand("sleep 1".split()),
                    ExtCommand(cmd_ssh_restart_cron.split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                ]),
            Stage("cleanup-after", 3, [
                Task("all", 0, [
                    ExtCommand((cmd_normal_load_base + " cleanup").split()),
                    ExtCommand((cmd_stress_load_base + " cleanup").split()),
                    ]),
                ])
            ])
    # todo - collect journalctl
    scenario.run()


if __name__ == "__main__":
    main()
