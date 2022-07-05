# Results

First test, against openshiftapps.com:
- cmd ./hello.py https://jc-sso-justin-cinkelj-dev.apps.sandbox.x8i5.p1.openshiftapps.com admin adminp 1000 >a.log 2>&1
- commit 87af00a292d7f980f8577cfd3ae03372ed28a2a5, keycloak-api@88af6cd438e4599ed3785261bb89324aa63a053d
- 1 user created in 0.32 sec
- 1000 users created in 12.22 sec
- equation is ~ 0.318+0.0120* N
Problems:
- each request opens new HTTPS connection
- 99% CPU usage with DEBUG log level
- 95% CPU usage with INFO log level
- token expires in 60 sec

Reuse requests connection
- commit d119273f48eff4d02fd9ca468616eb6b322af41e, keycloak-api@6ea60c79e691abe78b830b62f40da3c9b64ce72d
- 1000 users created in 4.174570 sec
- 10k users created in 41.397614 sec
- ~50% CPU usage with INFO log level
Problems:
- a few 10 "Connection pool is full, discarding connection" messages
