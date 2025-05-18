'''Dovecot Quotas API'''
import re
import logging
import socket
import paramiko

TIMEOUT = 10

GET_QUOTA_CMD = "doveadm quota get -A | grep STORAGE"
GET_DOVECOT_VERSION_CMD = "doveadm --version"

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
        output = await self.execute_command(GET_DOVECOT_VERSION_CMD)
        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        return version.group() if version else ""

    async def get_quotas(self):
        '''Get the quotas for all mailboxes.'''
        await self.update_quotas()
        return self._quotas

    async def update_quotas(self):
        '''Update the quotas for all mailboxes.'''
        self._quotas = {}

        result = await self.execute_command(GET_QUOTA_CMD)
        if not result:
            _LOGGER.error("Failed to execute command: %s", GET_QUOTA_CMD)
            return

        quotas = {}
        for line in result.splitlines():
            mailbox, *_, used, quota, percentage_used = re.split(r" {1,}", line)
            quotas[mailbox] = {
                'name': mailbox,
                'used': float(used),
                'quota': float(quota) if quota != '-' else None,
                'percentage_used': float(percentage_used) if quota != '-' else None,
                'free': float(quota) - float(used) if quota != '-' else None,
                'percentage_free': 100 - float(percentage_used) if quota != '-' else None,
            }
        self._quotas = quotas

    async def test_connection(self):
        '''Test the SSH connection to the server.'''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self._hostname,
            username=self._username,
            password=self._password,
            timeout=TIMEOUT
        )
        ssh.close()

    async def execute_command(self, command: str) -> str:
        '''Execute a command on the server via SSH.'''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                self._hostname,
                username=self._username,
                password=self._password,
                timeout=TIMEOUT
            )
        except (paramiko.SSHException, socket.timeout) as e:
            _LOGGER.error("SSH connection failed: %s", e)
            return
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        ssh_stdin.close()
        ssh_stderr.close()
        output = ssh_stdout.read().decode()
        ssh.close()
        return output
