#!/usr/bin/env python

import os
import paramiko
import argparse

output_file = 'out_paramiko.txt'
port = '22'


def parse_args():

    parser = argparse.ArgumentParser(description='Retrieve args')
    parser.add_argument('--hostname', required=True)
    parser.add_argument('--username', required=False, default=os.environ['USER'])
    parser.add_argument('--pkey', required=False)
    parser.add_argument('--command', required=True)
    parser.add_argument('--service', required=True)
    args = parser.parse_args()
    return args

def connection():

    args = parse_args()
    client = paramiko.client.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    # client.connect(hostname=host, username=username, password=password, allow_agent=False, look_for_keys=False)
    # client.connect(hostname=args.hostname, port=port, username=args.username, key_filename=args.pkey, allow_agent=False, look_for_keys=False)

    # with allow_agent=True, the key_filename is not really used
    client.connect(hostname=args.hostname, port=port, username=args.username, key_filename=args.pkey, allow_agent=True, look_for_keys=False)

    return client


def main():

    client = connection()
    args = parse_args()
    cmd = [args.command, args.service]
    execute = ' '.join(cmd)
    (stdin, stdout, stderr) = client.exec_command(execute)
    # (stdin, stdout, stderr) = client.exec_command("sudo systemctl status crond")

    cmd_output = stdout.read().decode()
    print('log printing: ', cmd_output)
    print(f'exit code: {stdout.channel.recv_exit_status()}')

    # TODO what we want in output file:
    #   time of execution
    #   command that was executed,
    #   exit code of the executed command
    #   service status before/after
    # Maybe call should be
    # ./sys_command.py --hostname jcpc --username root --pkey $HOME/.ssh/id_rsa --service crond --action start
    with open(output_file, "w+") as file:
        file.write(str(cmd_output))

    client.close()


if __name__ == "__main__":
    main()
