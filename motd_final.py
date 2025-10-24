import subprocess
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

STUDENT_ID = "66070136"
username = "admin"
password = "cisco"


def set_motd(router_ip, motd_text):
    """Configure MOTD using Ansible"""
    # Get the absolute path to the ansible-playbook in virtual environment
    venv_ansible = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'ansible-playbook')
    
    # Use the virtual environment's ansible-playbook if it exists, otherwise use system ansible-playbook
    if os.path.exists(venv_ansible):
        command = [
            venv_ansible, 
            'configure_motd.yaml', 
            '--limit', router_ip,
            '-e', f'motd_text="{motd_text}"'
        ]
    else:
        command = [
            'ansible-playbook', 
            'configure_motd.yaml', 
            '--limit', router_ip,
            '-e', f'motd_text="{motd_text}"'
        ]
    
    # Change to the script directory to ensure relative paths work
    script_dir = os.path.dirname(__file__)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=script_dir, timeout=60)
        result_output = result.stdout + result.stderr
        
        print("Ansible MOTD output:")
        print(result_output)
        
        # Check if ansible ran successfully
        if result.returncode == 0 and 'failed=0' in result_output:
            return 'Ok: success'
        else:
            return 'Error: Ansible failed to configure MOTD'
    except subprocess.TimeoutExpired:
        return 'Error: Ansible timeout'
    except Exception as e:
        print(f"Error running ansible: {e}")
        return 'Error: Ansible execution failed'


def get_motd(router_ip):
    """Get MOTD using Netmiko"""
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
        "conn_timeout": 20,
        "timeout": 20,
    }
    
    try:
        with ConnectHandler(**device_params) as ssh:
            # Get running config and extract MOTD
            output = ssh.send_command("show running-config | section banner motd")
            
            if not output or "banner motd" not in output.lower():
                return "Error: No MOTD Configured"
            
            # Parse MOTD text
            # MOTD format in config:
            # banner motd ^C
            # Your MOTD text here
            # ^C
            lines = output.split('\n')
            motd_lines = []
            in_motd = False
            delimiter = None
            
            for line in lines:
                if line.startswith('banner motd'):
                    in_motd = True
                    # Extract delimiter (character after 'banner motd ')
                    parts = line.split('banner motd')
                    if len(parts) > 1 and len(parts[1].strip()) > 0:
                        delimiter = parts[1].strip()[0]
                        # Check if MOTD text is on the same line
                        remaining = parts[1].strip()[1:].strip()
                        if remaining and remaining != delimiter:
                            motd_lines.append(remaining)
                    continue
                
                if in_motd:
                    # Check if line contains ending delimiter
                    if delimiter and delimiter in line:
                        # Get text before delimiter
                        text_before = line.split(delimiter)[0]
                        if text_before.strip():
                            motd_lines.append(text_before.strip())
                        break
                    else:
                        if line.strip():
                            motd_lines.append(line.strip())
            
            if motd_lines:
                motd_text = ' '.join(motd_lines)
                return motd_text
            else:
                return "Error: No MOTD Configured"
                
    except NetmikoTimeoutException:
        return f"Error: Connection timeout to router {router_ip}"
    except NetmikoAuthenticationException:
        return f"Error: Authentication failed to router {router_ip}"
    except Exception as e:
        print(f"Error: {e}")
        return "Error: Unable to retrieve MOTD"
