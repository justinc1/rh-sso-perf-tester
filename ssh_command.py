#!/usr/bin/env python

import os
import sys
import paramiko
import argparse
import logging

output_file = 'out_paramiko.txt'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Execute commands via SSH.'
                    ' Helps to login with passphrase protected SSH key, non-interactively.')
    # SSH connection paramters
    parser.add_argument('--hostname', required=True,
                        help='Host to SSH to')
    parser.add_argument('--port', type=int, default=22,
                        help='SSH port')
    parser.add_argument('--username', required=False, default=os.environ['USER'],
                        help='SSH username')
    parser.add_argument('--pkey', required=True,
                        help='SSH private key')
    parser.add_argument('--passphrase', required=False, default=os.environ.get("SSHPASS"),
                        help='Passphrase for SSH key. By default environ variable SSHPASS will be used (if set).')
    # Parameters for executed command
    parser.add_argument('--sudo_password', required=True,
                        help='Password to be used for sudo.')
    parser.add_argument('--command', required=True, nargs='+',
                         help='Command to execute (as root user - with sudo)')
    args = parser.parse_args()
    return args


def connection(hostname, port, username, pkey, passphrase):
    client = paramiko.client.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    pkey_decrypted_content = paramiko.RSAKey.from_private_key(open(pkey), passphrase)
    client.connect(hostname=hostname, port=port, username=username, pkey=pkey_decrypted_content, allow_agent=False, look_for_keys=False)
    return client


def main():
    args = parse_args()
    client = connection(args.hostname, args.port, args.username, args.pkey, args.passphrase)
    ssh_param_description = f"hostname={args.hostname} port={args.port} username={args.username} pkey={args.pkey}"
    print(f"SSH connection: {ssh_param_description}")

#     systemctl_cmd = ['systemctl', args.action, args.service]
    command = args.command
    sudo_cmd = ['sudo', '-S']
    # execute = ' '.join(sudo_cmd + ['whoami'])  # a safe test
    execute = ' '.join(sudo_cmd + command)
    print(f"Command: {execute}")

    # https://stackoverflow.com/questions/48554497/how-do-i-write-to-stdin-returned-from-exec-command-in-paramiko
    (stdin, stdout, stderr) = client.exec_command(execute)
    stdin.channel.send(args.sudo_password + "\n")
    stdin.channel.shutdown_write()

    stdout_content = stdout.read().decode()
    stderr_content = stderr.read().decode()
    print(f'exit code: {stdout.channel.recv_exit_status()}')
    print('stdout_content: ', stdout_content)
    print('stderr_content: ', stderr_content)

    # TODO what we want in output file:
    #   time of execution
    #   command that was executed,
    #   exit code of the executed command
    #   service status before/after
    # Maybe call should be
    # ./sys_command.py --hostname jcpc --username root --pkey $HOME/.ssh/id_rsa --service crond --action start
    with open(output_file, "w+") as file:
        file.write(str(stdout_content))
        file.write(str(stderr_content))

    client.close()


if __name__ == "__main__":
    main()
