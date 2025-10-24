from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from pprint import pprint
import subprocess
import os

username = "admin"
password = "cisco"


def gigabit_status(router_ip):
    """Get the status of all GigabitEthernet interfaces"""
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
        "conn_timeout": 20,  # Connection timeout (default: 10)
        "timeout": 20,       # Command timeout (default: 100, but be conservative)
    }
    
    try:
        ans = ""
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0
            result = ssh.send_command("show ip interface brief", use_textfsm=True)
            
            # Check if result is valid
            if not result or not isinstance(result, list):
                return "Error: Unable to retrieve interface information"
            
            for interface in result:
                # TextFSM returns 'interface' key (lowercase), not 'intf'
                if interface.get('interface', '').startswith('GigabitEthernet'):
                    interface_name = interface['interface']
                    status = interface.get('status', 'unknown')
                    
                    if status == "up":
                        up += 1
                        ans += f"{interface_name} up, "
                    elif status == "down":
                        down += 1
                        ans += f"{interface_name} down, "
                    elif status == "administratively down":
                        admin_down += 1
                        ans += f"{interface_name} administratively down, "
            
            # Remove trailing comma and space
            ans = ans.rstrip(', ')
            
            # Add summary
            summary = f" -> {up} up, {down} down, {admin_down} administratively down"
            ans += summary
            
            pprint(ans)
            return ans
            
    except NetmikoTimeoutException as e:
        error_msg = f"Error: Connection timeout to router {router_ip}. Please check network connectivity."
        print(error_msg)
        return error_msg
    except NetmikoAuthenticationException as e:
        error_msg = f"Error: Authentication failed to router {router_ip}."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error: Unable to get interface status - {str(e)}"
        print(error_msg)
        return error_msg
def set_motd(router_ip, motd_text):
    """Configure MOTD using Ansible"""
    command = [
        'ansible-playbook', 
        'configure_motd.yaml', 
        '--limit', router_ip,
        '-e', f'motd_text="{motd_text}"'
    ]
    
    script_dir = os.path.dirname(__file__)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=script_dir, timeout=60)
        output = result.stdout + result.stderr
        
        if result.returncode == 0 and 'failed=0' in output:
            return 'Ok: success'
        else:
            return 'Error: Ansible failed'
    except subprocess.TimeoutExpired:
        return 'Error: Timeout'
    except Exception:
        return 'Error: Execution failed'


def get_motd(router_ip):
    """Get MOTD using Netmiko with TextFSM"""
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
    }
    
    try:
        with ConnectHandler(**device_params) as ssh:
            # Use show banner motd to get MOTD
            output = ssh.send_command("show banner motd")
            
            if not output:
                return "Error: No MOTD Configured"
            
            # Check for no banner configured
            if "no motd banner" in output.lower() or "invalid input" in output.lower():
                return "Error: No MOTD Configured"
            
            # Parse output line by line
            lines = []
            for line in output.splitlines():
                stripped = line.strip()
                # Skip empty lines
                if not stripped:
                    continue
                # Skip delimiter lines (^C, ^, etc.)
                if stripped in ["^C", "^"]:
                    continue
                # Skip banner command echo
                if stripped.lower().startswith("banner motd"):
                    continue
                lines.append(stripped)
            
            if not lines:
                return "Error: No MOTD Configured"
            
            # Join all lines with space
            return ' '.join(lines)
                
    except (NetmikoTimeoutException, NetmikoAuthenticationException):
        return "Error: Connection failed"
    except Exception:
        return "Error: Unable to retrieve MOTD"
