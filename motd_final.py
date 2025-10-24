import subprocess
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

STUDENT_ID = "66070136"
username = "admin"
password = "cisco"


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
