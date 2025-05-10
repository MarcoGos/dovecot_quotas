from typing import Any
import re
import paramiko
import logging
import socket
from pathlib import Path

TIMEOUT = 10

cmd_to_execute = "doveadm quota get -A | grep STORAGE"

_LOGGER = logging.getLogger(__name__)

class QuotasAPI:
    _quotas = {}
    _hostname: str
    _username: str
    _password: str
    def __init__(self, hostname: str, username: str, password:str):
        self._hostname = hostname
        self._username = username
        self._password = password

    async def get_quotas(self):
        await self.update_quotas()
        return self._quotas

    async def update_quotas(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _LOGGER.debug("Connecting to %s with %s and <password>", self._hostname, self._username)
        ssh.connect(self._hostname, username=self._username, password=self._password, look_for_keys=False, allow_agent=False)
        _LOGGER.debug("Connected to %s with %s and <password>", self._hostname, self._username)
        _LOGGER.debug("Executing command: %s", cmd_to_execute)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
        _LOGGER.debug("Command executed: %s", cmd_to_execute)
        ssh_stdin.close()
        ssh_stderr.close()

        quotas = {}
        for line in ssh_stdout.read().decode().splitlines():
            mailbox, _, _, _, used, quota, percentage_used = re.split(r" {1,}", line)
            quotas[mailbox] = {
                'name': mailbox,
                'used': used,
                'quota': quota if quota != '-' else quota,
                'percentage_used': percentage_used
            }
        ssh.close()
        _LOGGER.debug("Quotas: %s", quotas)
        self._quotas = quotas
