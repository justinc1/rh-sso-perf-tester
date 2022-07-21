# Usage

Start test SSO server at https://developers.redhat.com/developer-sandbox/get-started.

```
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export APIURL=https://jc-sso-justin-cinkelj-dev.apps.sandbox.x8i5.p1.openshiftapps.com
export APIURL=https://sso-minh-tran-duc-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com

./stress_test.py --url $APIURL --username admin --password admin_pass --workers 4 --requests 10
./normal_load.py --url $APIURL --username admin --password admin_pass --iter 3 --period 10 --action login
./sys_command.py --hostname jcpc --username $USER --pkey $HOME/.ssh/id_rsa --command 'systemctl status' --service crond

# sample scenario - does not require SSO, only echo and similar commands are run
./sample_scenario_01.py main

# real scenario with normal and stress load for SSO server
export SSO_API_USERNAME=admin
export SSO_API_PASSWORD=admin_pass
./scenario_02.py
```
