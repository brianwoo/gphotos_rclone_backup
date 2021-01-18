#!/usr/bin/env python3

import sys
import os
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path


CURRENT_DIR = Path(os.getcwd())
CLIENT_SECRETS_FILE = CURRENT_DIR / "client_secret.json"
TOKEN_FILE = CURRENT_DIR / "gmail_token.json"
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=OAUTH_SCOPE)

def main():
    store = file.Storage(TOKEN_FILE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=OAUTH_SCOPE)
        creds = tools.run_flow(flow, store, tools.argparser.parse_args())
    discovery.build('gmail', 'v1', http=creds.authorize(Http()))    


if __name__ == "__main__":
    main()