#!/usr/bin/env python

import os
import time
import sys
import logging
from datetime import datetime, timezone
from scenario import ExtCommand, Task, Stage, Scenario
from inventory import SampleInventory

LOGGING_LEVEL = logging.DEBUG
# LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(process)d %(message)s'
logging.basicConfig(
    level=LOGGING_LEVEL,
    format=LOGGING_FORMAT,
)
logger = logging.getLogger(__name__)


class JournalcmdGenerator:
    def __init__(self):
        self.start_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def get(self, service=None):
        # --until is not used - .get() is called when
        # scenario/stages/tasks are created, not when they are run.
        cmd = f"journalctl --since '{self.start_time}'"
        if service:
            cmd += f" -u {service}"
        return cmd


def main():
    inventory = SampleInventory()

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

    jcmd = JournalcmdGenerator()
    scenario = Scenario(
        "sc02", stages=[
            Stage("cleanup-before", [
                Task("all", [
                    ExtCommand((cmd_normal_load_base + " cleanup").split()),
                    ExtCommand((cmd_stress_load_base + " cleanup").split()),
                    ]),
                ]),
            Stage("prepare", [
                Task("all", [
                    ExtCommand((cmd_normal_load_base + " prepare").split()),
                    ExtCommand((cmd_stress_load_base + " prepare" + cmd_stress_load_test).split()),
                    ]),
                ]),
            Stage("test", [
                Task("normal_load", [
                    ExtCommand("sleep 1".split()),
                    ExtCommand((cmd_normal_load_base + " test" + cmd_normal_load_test).split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                Task("stress_load", [
                    ExtCommand("sleep 1".split()),
                    ExtCommand((cmd_stress_load_base + " test" + cmd_stress_load_test).split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                Task("restart_crond", [
                    ExtCommand("sleep 1".split()),
                    ExtCommand(cmd_ssh_restart_cron.split()),
                    ExtCommand("sleep 1".split()),
                    ]),
                ]),
            Stage("logs", [
                Task(host.name, [
                    ExtCommand((cmd_ssh_base + f" --hostname {host.address} --command \"{jcmd.get()}\"").split()),
                    ExtCommand((cmd_ssh_base + f" --hostname {host.address} --command \"{jcmd.get('crond')}\"").split()),
                    ExtCommand((cmd_ssh_base + f" --hostname {host.address} --command /bin/cat /etc/issue").split()),
                    ])
                for host in inventory.hosts()
                ] + [
                Task(host.name, [
                    ExtCommand((cmd_ssh_base + f" --hostname {host.address} --command echo Log from SSO app").split()),
                    ])
                for host in inventory.hosts("app")
                ] + [
                Task(host.name, [
                    ExtCommand((cmd_ssh_base + f" --hostname {host.address} --command echo Log from SSO DB").split()),
                    ])
                for host in inventory.hosts("db")
                ]
            ),
            Stage("cleanup-after", [
                Task("all", [
                    ExtCommand((cmd_normal_load_base + " cleanup").split()),
                    ExtCommand((cmd_stress_load_base + " cleanup").split()),
                    ]),
                ]),
            ])
    scenario.run()


if __name__ == "__main__":
    main()
