#!/usr/bin/env python

import os
import logging
from datetime import datetime
import asyncio
import re

LOGGING_LEVEL = logging.DEBUG
# LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(process)d %(message)s'
logging.basicConfig(
    level=LOGGING_LEVEL,
    format=LOGGING_FORMAT,
)
logger = logging.getLogger(__name__)


# make name suitable for filesystem path
def sanitize_path(name):
    return re.sub(r'[^\w\-_\./]', '-', name)


class ExtCommand:
    def __init__(self, argv):
        self._argv = argv
        self._process = None

    async def run(self, logfile):
        logfile.flush()
        # os.environ.update({"AA": "aa-updated"})
        cmd_str = " ".join(self._argv)
        self._process = await asyncio.create_subprocess_shell(cmd_str, stdin=None, stdout=logfile, stderr=logfile)
        logfile.flush()
        await self._process.communicate()
        logfile.flush()

    @property
    def cmd(self):
        return " ".join(self._argv)

    @property
    def returncode(self):
        if not self._process:
            return None
        return self._process.returncode


class Task:
    def __init__(self, name: str, task_id: int):
        self.name = name
        self.id = task_id
        self._commands = []

    async def run(self, logfile_path):
        with open(logfile_path, "w") as logfile:
            for command in self._commands:
                logger.debug(f"Running command: {command.cmd}")
                logfile.write(f"{datetime.utcnow()} command: {command.cmd}\n")
                await command.run(logfile)
                logfile.flush()


class Stage:
    def __init__(self, name: str, stage_id: int):
        self.name = name
        self.id = stage_id
        self._tasks = []

    async def run(self, logdir):
        # TODO - logfile per Task.
        # log filename: sc0-$date/s0-t0-sName-tName.log
        # include header
        as_tasks = []
        for task in self._tasks:
            logfile_path = os.path.join(logdir, f"s{self.id}-t{task.id}-{sanitize_path(self.name)}-{sanitize_path(task.name)}.log")
            as_tasks.append(asyncio.create_task(task.run(logfile_path)))
        [await as_task for as_task in as_tasks]


class Scenario:
    def __init__(self, name):
        self.name = name
        self._stages = []

    def run(self):
        main_logdir = "logs"
        date_str = datetime.strftime(datetime.utcnow(), "%Y%m%d-%H%M%S")
        logdir = os.path.join(main_logdir, f"{sanitize_path(self.name)}-{date_str}")
        os.mkdir(logdir)
        for stage in self._stages:
            asyncio.run(stage.run(logdir))
