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
    argv_normal_load = f"./normal_load.py {sso_url_user_pass} --iter 12 --period 5 --action login".split()
    argv_stress_load = f"./stress_test.py {sso_url_user_pass} --workers 1".split()
    if 1:
        argv_stress_load += "--requests 1000".split()
    else:
        argv_stress_load += "--requests 60 --period 1".split()

    scenario = Scenario(
        "sc02", stages=[
            Stage("prepare", 0),
            Stage("test", 1, [
                Task("normal_load", 0, [
                    ExtCommand("sleep 1".split()),
                    ExtCommand(argv_normal_load),
                    ExtCommand("sleep 1".split()),
                    ]),
                Task("stress_load", 1, [
                    ExtCommand("sleep 1".split()),
                    ExtCommand(argv_stress_load),
                    ExtCommand("sleep 1".split()),
                    ]),
                ]),
            ])
    # todo - collect journalctl
    scenario.run()


if __name__ == "__main__":
    main()
