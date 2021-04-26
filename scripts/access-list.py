#!/usr/bin/env python3
import os
import requests
import sys

if len(sys.argv) == 1:
    print("""Usage:\nOne argument - CloudID\n./access-list.py b1g*******""")
    sys.exit(0)

try:
    OAUTH = os.environ['OAUTH']
except KeyError:
    print("env OAUTH not set")
    sys.exit(1)

CLOUDID = sys.argv[1]
RMENDPOINT = 'https://resource-manager.api.cloud.yandex.net/resource-manager/v1/'
IAMENDPOINT = 'https://iam.api.cloud.yandex.net/iam/v1/userAccounts/'
TOKENENDPOINT = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'


def getiamtoken(oauth):
    # https://cloud.yandex.ru/docs/iam/api-ref/IamToken/create
    headers = {"yandexPassportOauthToken": oauth}
    request = requests.post(url=TOKENENDPOINT, params=headers)
    data = request.json()
    iamtoken = data.get('iamToken')
    return iamtoken


def getfolderaccesslist(folder, iamtoken):
    # https://cloud.yandex.ru/docs/resource-manager/api-ref/Folder/listAccessBindings
    params = {'pageSize': 1000}
    headers = {'Authorization': f'Bearer {iamtoken}'}
    request = requests.get(url=RMENDPOINT+'folders'+f'/{folder}:listAccessBindings',
                           headers=headers,
                           params=params)
    accesslist = request.json().get('accessBindings', [])
    return accesslist


def getfolderlist(cloudid, iamtoken):
    # https://cloud.yandex.ru/docs/resource-manager/api-ref/Folder/list
    params = {'cloudId': cloudid,
              'pageSize': 1000}
    headers = {'Authorization': f'Bearer {iamtoken}'}
    request = requests.get(url=RMENDPOINT+'folders',
                           params=params,
                           headers=headers)
    folderlist = request.json()['folders']
    return folderlist


def getcloudaccesslist(cloudid, iamtoken):
    # https://cloud.yandex.ru/docs/resource-manager/api-ref/Cloud/listAccessBindings
    params = {'pageSize': 1000}
    headers = {'Authorization': f'Bearer {iamtoken}'}
    request = requests.get(url=RMENDPOINT+'clouds'+f'/{cloudid}:listAccessBindings',
                           headers=headers,
                           params=params)
    accesslist = request.json().get('accessBindings', [])
    return accesslist


iamtoken = getiamtoken(OAUTH)
folderlist = getfolderlist(CLOUDID, iamtoken)
cloudaccesslist = getcloudaccesslist(CLOUDID, iamtoken)
folderaccesslist = {}
for folder in [data['id'] for data in folderlist]:
    folderaccesslist[folder] = getfolderaccesslist(folder, iamtoken)

accounts = {}

for folder in folderaccesslist.keys():
    for access in folderaccesslist[folder]:
        id = access['subject']['id']
        if id not in accounts.keys():
            accounts[id] = {}
            accounts[id]['type'] = access['subject']['type']
            accounts[id]['folders'] = {folder: []}
        if folder not in accounts[id]['folders'].keys():
            accounts[id]['folders'][folder] = []
        accounts[id]['folders'][folder].append(access['roleId'])

for access in cloudaccesslist:
    id = access['subject']['id']
    if id not in accounts.keys():
        accounts[id] = {}
        accounts[id]['type'] = access['subject']['type']
        accounts[id]['cloud'] = []
    try:
        accounts[id]['cloud'].append(access['roleId'])
    except:
        accounts[id]['cloud'] = []
        accounts[id]['cloud'].append(access['roleId'])

for userid in accounts:
    # https://cloud.yandex.ru/docs/iam/api-ref/UserAccount/get
    headers = {'Authorization': f'Bearer {iamtoken}'}
    if accounts[userid]['type'] != 'userAccount':
        accounts[userid]['login'] = None
        continue
    request = requests.get(url=IAMENDPOINT+userid, headers=headers)
    try:
        login = request.json()['yandexPassportUserAccount']['login']
    except KeyError:
        login = request.json()['samlUserAccount']['nameId']
    accounts[userid]['login'] = login

for account in accounts:
    acc = accounts[account]
    print(f'ID: {account}, type: {acc["type"]}, login: {acc["login"]}')
    try:
        print(f'Cloud roles: {", ".join(acc.get("cloud", ""))}')
        for folder in acc['folders']:
            for i in folderlist:
                if i['id'] == folder:
                    print(f'Folder ID: {folder}, Folder name: {i["name"]}, Roles: {", ".join(acc["folders"][folder])}')
    except KeyError as err:
        print(err)
        sys.exit(1)
    print()
