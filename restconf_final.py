import json
import requests
requests.packages.urllib3.disable_warnings()


STUDENT_ID = "66070136"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create(router_ip):
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{STUDENT_ID}"
    
    # Check if interface already exists
    check_resp = requests.get(
        api_url,
        auth=basicauth,
        headers=headers,
        verify=False
    )
    
    if check_resp.status_code == 200:
        # Interface already exists
        print("Interface already exists")
        return f"Cannot create: Interface loopback {STUDENT_ID}"
    
    # Calculate IP address from student ID
    last_three = STUDENT_ID[-3:]  # Get last 3 digits
    x = int(last_three[0])
    y = int(last_three[1:])
    ip_address = f"172.{x}.{y}.1"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{STUDENT_ID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip_address,
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }

    resp = requests.put(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {STUDENT_ID} is created successfully using Restconf"
    elif(resp.status_code == 409):
        print("Interface already exists: {}".format(resp.status_code))
        return f"Cannot create: Interface loopback {STUDENT_ID}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot create: Interface loopback {STUDENT_ID}"


def delete(router_ip):
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{STUDENT_ID}"
    
    resp = requests.delete(
        api_url, 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {STUDENT_ID} is deleted successfully using Restconf"
    elif(resp.status_code == 404):
        print("Interface not found: {}".format(resp.status_code))
        return f"Cannot delete: Interface loopback {STUDENT_ID}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface loopback {STUDENT_ID}"


def enable(router_ip):
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{STUDENT_ID}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{STUDENT_ID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True
        }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {STUDENT_ID} is enabled successfully using Restconf"
    elif(resp.status_code == 404):
        print("Interface not found: {}".format(resp.status_code))
        return f"Cannot enable: Interface loopback {STUDENT_ID}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot enable: Interface loopback {STUDENT_ID}"


def disable(router_ip):
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{STUDENT_ID}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{STUDENT_ID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False
        }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {STUDENT_ID} is shutdowned successfully using Restconf"
    elif(resp.status_code == 404):
        print("Interface not found: {}".format(resp.status_code))
        return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Restconf)"


def status(router_ip):
    api_url_status = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{STUDENT_ID}"

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json['ietf-interfaces:interface']['admin-status']
        oper_status = response_json['ietf-interfaces:interface']['oper-status']
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface loopback {STUDENT_ID} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface loopback {STUDENT_ID} is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface loopback {STUDENT_ID} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"No Interface loopback {STUDENT_ID} (checked by Restconf)"
