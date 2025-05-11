'''Dovecot Quotas API'''
import re
import logging
import socket
from pathlib import Path
import paramiko

TIMEOUT = 10

get_quota_cmd = "doveadm quota get -A | grep STORAGE"

_LOGGER = logging.getLogger(__name__)

class QuotasAPI:
    '''Class to interact with the Dovecot Quotas API.'''
    _quotas = {}
    _hostname: str
    _username: str
    _password: str
    def __init__(self, hostname: str, username: str, password:str):
        self._hostname = hostname
        self._username = username
        self._password = password

    async def get_version(self) -> str:
        '''Get the version of Dovecot installed on the server.'''
        output = await self.execute_command("dovecot --version")
        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        return version.group() if version else ""

    async def get_quotas(self):
        '''Get the quotas for all mailboxes.'''
        await self.update_quotas()
        return self._quotas

    async def update_quotas(self):
        '''Update the quotas for all mailboxes.'''
        self._quotas = {}

        result = await self.execute_command(get_quota_cmd)
        if not result:
            _LOGGER.error("Failed to execute command: %s", get_quota_cmd)
            return

        quotas = {}
        for line in result.splitlines():
            mailbox, _, _, _, used, quota, percentage_used = re.split(r" {1,}", line)
            quotas[mailbox] = {
                'name': mailbox,
                'used': used,
                'quota': quota if quota != '-' else quota,
                'percentage_used': percentage_used
            }
        self._quotas = quotas

    async def test_connection(self):
        '''Test the SSH connection to the server.'''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self._hostname, username=self._username, password=self._password, timeout=TIMEOUT)
        ssh.close()

    async def execute_command(self, command: str) -> str:
        '''Execute a command on the server via SSH.'''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self._hostname, username=self._username, password=self._password, timeout=TIMEOUT)
        except (paramiko.SSHException, socket.timeout) as e:
            _LOGGER.error(f"SSH connection failed: {e}")
            return
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        ssh_stdin.close()
        ssh_stderr.close()
        output = ssh_stdout.read().decode()
        ssh.close()
        return output
