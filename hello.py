#!/usr/bin/env python

import logging
import sys
import kcapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("ttrt")
    api_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    realm = "master"

    oid_client = kcapi.OpenID({
        "client_id": "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password",
        "realm" : realm
    }, api_url)
    token = oid_client.getToken()
    # 'expires_in': 60,
    kc = kcapi.Keycloak(token, api_url)
    users = kc.build("users", realm)
    logger.info(f"User count: {len(users.all())}")
    uu1 = users.findFirst({"key":"username", "value": "user000001"})
    logger.info(f"User 01:: {uu1}")


if __name__ == "__main__":
    main()
