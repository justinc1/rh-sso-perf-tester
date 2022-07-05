# Results

First test, against openshiftapps.com:
- cmd ./hello.py https://jc-sso-justin-cinkelj-dev.apps.sandbox.x8i5.p1.openshiftapps.com admin adminp 1000 >a.log 2>&1
- commit 87af00a292d7f980f8577cfd3ae03372ed28a2a5
- 1 user created in 0.32 sec
- 1000 users created in 12.22 sec
- equation is ~ 0.318+0.0120* N

Problems:
- each request opens new HTTPS connection
- 99% CPU usage with DEBUG log level
- 95% CPU usage with INFO log level
- token expires in 60 sec
