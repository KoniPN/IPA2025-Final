from ncclient import manager
import xmltodict
from ncclient.operations.rpc import RPCError

STUDENT_ID = "66070136"
username = "admin"
password = "cisco"
netconf_port = 830


def create(router_ip):
    """Create loopback interface using NETCONF"""
    # Calculate IP address from student ID
    last_three = STUDENT_ID[-3:]  # Get last 3 digits
    x = int(last_three[0])
    y = int(last_three[1:])
    ip_address = f"172.{x}.{y}.1"
    
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{STUDENT_ID}</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>{ip_address}</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
            </interface>
        </interfaces>
    </config>
    """
    
    try:
        m = manager.connect(
            host=router_ip,
            port=netconf_port,
            username=username,
            password=password,
            hostkey_verify=False
        )
        
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        m.close_session()
        
        if '<ok/>' in netconf_reply.xml:
            return f"Interface loopback {STUDENT_ID} is created successfully using Netconf"
        else:
            return f"Cannot create: Interface loopback {STUDENT_ID}"
    except RPCError as e:
        if 'data-exists' in str(e):
            return f"Cannot create: Interface loopback {STUDENT_ID}"
        else:
            print(f"NETCONF Error: {e}")
            return f"Cannot create: Interface loopback {STUDENT_ID}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Cannot create: Interface loopback {STUDENT_ID}"


def delete(router_ip):
    """Delete loopback interface using NETCONF"""
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback{STUDENT_ID}</name>
            </interface>
        </interfaces>
    </config>
    """
    
    try:
        m = manager.connect(
            host=router_ip,
            port=netconf_port,
            username=username,
            password=password,
            hostkey_verify=False
        )
        
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        m.close_session()
        
        if '<ok/>' in netconf_reply.xml:
            return f"Interface loopback {STUDENT_ID} is deleted successfully using Netconf"
        else:
            return f"Cannot delete: Interface loopback {STUDENT_ID}"
    except RPCError as e:
        if 'data-missing' in str(e) or 'invalid-value' in str(e):
            return f"Cannot delete: Interface loopback {STUDENT_ID}"
        else:
            print(f"NETCONF Error: {e}")
            return f"Cannot delete: Interface loopback {STUDENT_ID}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Cannot delete: Interface loopback {STUDENT_ID}"


def enable(router_ip):
    """Enable (no shutdown) loopback interface using NETCONF"""
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{STUDENT_ID}</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """
    
    try:
        m = manager.connect(
            host=router_ip,
            port=netconf_port,
            username=username,
            password=password,
            hostkey_verify=False
        )
        
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        m.close_session()
        
        if '<ok/>' in netconf_reply.xml:
            return f"Interface loopback {STUDENT_ID} is enabled successfully using Netconf"
        else:
            return f"Cannot enable: Interface loopback {STUDENT_ID}"
    except RPCError as e:
        if 'data-missing' in str(e) or 'invalid-value' in str(e):
            return f"Cannot enable: Interface loopback {STUDENT_ID}"
        else:
            print(f"NETCONF Error: {e}")
            return f"Cannot enable: Interface loopback {STUDENT_ID}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Cannot enable: Interface loopback {STUDENT_ID}"


def disable(router_ip):
    """Disable (shutdown) loopback interface using NETCONF"""
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{STUDENT_ID}</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """
    
    try:
        m = manager.connect(
            host=router_ip,
            port=netconf_port,
            username=username,
            password=password,
            hostkey_verify=False
        )
        
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        m.close_session()
        
        if '<ok/>' in netconf_reply.xml:
            return f"Interface loopback {STUDENT_ID} is shutdowned successfully using Netconf"
        else:
            return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Netconf)"
    except RPCError as e:
        if 'data-missing' in str(e) or 'invalid-value' in str(e):
            return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Netconf)"
        else:
            print(f"NETCONF Error: {e}")
            return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return f"Cannot shutdown: Interface loopback {STUDENT_ID} (checked by Netconf)"


def status(router_ip):
    """Check loopback interface status using NETCONF"""
    netconf_filter = f"""
    <filter>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{STUDENT_ID}</name>
            </interface>
        </interfaces-state>
    </filter>
    """
    
    try:
        m = manager.connect(
            host=router_ip,
            port=netconf_port,
            username=username,
            password=password,
            hostkey_verify=False
        )
        
        netconf_reply = m.get(filter=netconf_filter)
        m.close_session()
        
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)
        
        # Check if interface data exists
        if netconf_reply_dict.get('rpc-reply', {}).get('data', {}).get('interfaces-state'):
            interface_data = netconf_reply_dict['rpc-reply']['data']['interfaces-state'].get('interface')
            
            if interface_data:
                admin_status = interface_data.get('admin-status', 'down')
                oper_status = interface_data.get('oper-status', 'down')
                
                if admin_status == 'up' and oper_status == 'up':
                    return f"Interface loopback {STUDENT_ID} is enabled (checked by Netconf)"
                elif admin_status == 'down' and oper_status == 'down':
                    return f"Interface loopback {STUDENT_ID} is disabled (checked by Netconf)"
                else:
                    return f"Interface loopback {STUDENT_ID} is disabled (checked by Netconf)"
            else:
                return f"No Interface loopback {STUDENT_ID} (checked by Netconf)"
        else:
            return f"No Interface loopback {STUDENT_ID} (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return f"No Interface loopback {STUDENT_ID} (checked by Netconf)"
