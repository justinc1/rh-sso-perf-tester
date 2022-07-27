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


# Sample classes and a test
def write_one_msg(fout, msg):
    line = f"TESTPREFIX {datetime.utcnow()} {os.getpid()} {msg}\n"
    fout.write(line)
    fout.flush()


def sleep_write(argv):
    logger.debug(f"argv={argv}")
    delays = [float(argv[0]), float(argv[2])]
    msgs = [argv[1], argv[3]]
    # fout = open("test.log", "w")
    fout = sys.stdout
    write_one_msg(fout, f"Starting: sleep_write {argv}")
    for delay, msg in zip(delays, msgs):
        # logger.info(f"next ... cmd={argv}")
        write_one_msg(fout, msg)
        time.sleep(delay)
    write_one_msg(fout, f"Finished: sleep_write {argv}")


class SampleTask(Task):
    def __init__(self, name, task_id, stage_id, delay1, delay2):
        super().__init__(name)
        self._commands = [
            ExtCommand("/bin/echo asdf AA=${AA:-em-AA-not-defined} BB=${BB:-em-BB-not-defined}".split()),
            ExtCommand(
                f"./sample_scenario_01.py sleep_write"
                f" {delay1} s{stage_id}-t{task_id}-my-msg-1"
                f" {delay2} s{stage_id}-t{task_id}-my-msg-2".split()),
        ]


class SampleStage(Stage):
    def __init__(self, name, stage_id):
        super().__init__(name)
        self._tasks = [
            SampleTask("task0", 0, stage_id, 0.1, 0.2),
            SampleTask("task1", 1, stage_id, 0.2, 0.2),
            SampleTask("task2", 2, stage_id, 0.3, 0.7),
        ]


class SampleScenario(Scenario):
    def __init__(self):
        super().__init__("sample_scenario_01")
        self._stages = [
            SampleStage("stage0", 0),
            SampleStage("stage1", 1),
        ]


def test_scenario():
    scenario = SampleScenario()
    scenario.run()


# ====================================
def main(argv):
    print("In main")
    sys.stdout.flush()
    test_scenario()


def main_router():
    mode = sys.argv[1]
    if mode == "main":
        main(sys.argv[2:])
    elif mode == "sleep_write":
        sleep_write(sys.argv[2:])


if __name__ == "__main__":
    main_router()
