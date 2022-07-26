# Usage

Start test SSO server at https://developers.redhat.com/developer-sandbox/get-started.

```
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export APIURL=https://jc-sso-justin-cinkelj-dev.apps.sandbox.x8i5.p1.openshiftapps.com
export APIURL=https://sso-minh-tran-duc-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com

./stress_test.py --url $APIURL --username admin --password admin_pass cleanup
./stress_test.py --url $APIURL --username admin --password admin_pass prepare --workers 4 --users 10
./stress_test.py --url $APIURL --username admin --password admin_pass test --workers 4 --users 10
./stress_test.py --url $APIURL --username admin --password admin_pass cleanup

./normal_load.py --url $APIURL --username admin --password admin_pass cleanup
./normal_load.py --url $APIURL --username admin --password admin_pass prepare
./normal_load.py --url $APIURL --username admin --password admin_pass test --iter 3 --period 10 --action query
./normal_load.py --url $APIURL --username admin --password admin_pass test --iter 3 --period 10 --action login
./normal_load.py --url $APIURL --username admin --password admin_pass cleanup

export SSHPASS=pass2
# export SSHPASS=`cat`
#   passphrase, enter, ctrl+d
./sys_command.py --hostname localhost --username uu3 --pkey $HOME/.ssh/id_rsa2 --service crond --action restart --sudo_password uu3p

# sample scenario - does not require SSO, only echo and similar commands are run
./sample_scenario_01.py main

# real scenario with normal and stress load for SSO server
export SSO_API_USERNAME=admin
export SSO_API_PASSWORD=admin_pass
./scenario_02.py
```

## Setup test server

We want to test only:
 - SSH login with passphrase protected SSH key, passphrase is not provided by SSH agent.
 - sudo with password

SSH login:

```shell
# Create new ssh key, with passphrase.
ssh-keygen -f ~/.ssh/id_rsa2 -N pass2 -C test-key-passphrase-pass2

# Add new user, with sudo rights, sudo password required.
sudo useradd -G wheel uu3
echo uu3p | sudo passwd --stdin uu3
sudo mkdir -m 0700 /home/uu3/.ssh
sudo cat ~/.ssh/id_rsa2.pub | sudo dd of=/home/uu3/.ssh/authorized_keys
sudo chmod 0600 /home/uu3/.ssh/authorized_keys
sudo chown -R uu3:uu3 /home/uu3/.ssh
# sudo userdel -r uu3

# Test noninteractive login
export SSHPASS=pass2
unset SSH_AUTH_SOCK
sshpass -e -v -P passphrase ssh -i ~/.ssh/id_rsa2 uu3@localhost date
```
