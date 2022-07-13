# Usage

```
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

APIURL=https://jc-sso-justin-cinkelj-dev.apps.sandbox.x8i5.p1.openshiftapps.com
APIURL=https://sso-minh-tran-duc-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com

./hello.py --url $APIURL --username admin --password admin_pass --workers 4 --requests 10
./user_info.py --url $APIURL --username admin --password admin_pass --iter 3
./sys_command.py --hostname jcpc --username $USER --pkey $HOME/.ssh/id_rsa --command 'systemctl status' --service crond
```

