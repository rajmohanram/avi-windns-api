""""
Custom Windows DNS script
"""
#!/usr/bin/python3
import requests
from requests.auth import HTTPBasicAuth
import json

# URL of the Windows DNS API server
url = "https://dnsapi.cnalabs.com/api/record"


def CreateOrUpdateRecord(record_info, params):
    username = params.get('username')
    password = params.get('password')
    ip = record_info.get('f_ip_address', '') or record_info.get('ip_address', '')
    fqdn = record_info.get('fqdn')
    host = fqdn.split('.')[0]
    zone = '.'.join(fqdn.split('.')[1:])

    # REST API
    add_payload = json.dumps({"zone": zone, "host": host, "ip": ip})
    response = requests.post(url=url, data=add_payload, auth=HTTPBasicAuth(username, password),
                             timeout=15, verify=False)

    if not response.status_code == 201:
        err_str = "ERROR:"
        err_str += "   STATUS: " + response.json()
        print(err_str)
        raise Exception("DNS record update failed with %s"%err_str)


def DeleteRecord(record_info, params):
    username = params.get('username')
    password = params.get('password')
    fqdn = record_info.get('fqdn')
    host = fqdn.split('.')[0]
    zone = '.'.join(fqdn.split('.')[1:])

    # REST API
    del_payload = json.dumps({"zone": zone, "host": host})
    response = requests.delete(url=url, data=del_payload, auth=HTTPBasicAuth(username, password),
                               timeout=15, verify=False)

    if not response.status_code == 200:
        err_str = "ERROR:"
        err_str += "   STATUS: " + response.json()
        print(err_str)
        raise Exception("DNS record update failed with %s"%err_str)

