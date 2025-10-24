import subprocess
import os
import glob

def showrun(router_ip):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    # Get the absolute path to the ansible-playbook in virtual environment
    venv_ansible = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'ansible-playbook')
    
    # Use the virtual environment's ansible-playbook if it exists, otherwise use system ansible-playbook
    # Use --limit to target a specific router IP
    if os.path.exists(venv_ansible):
        command = [venv_ansible, 'backup_config.yaml', '--limit', router_ip]
    else:
        command = ['ansible-playbook', 'backup_config.yaml', '--limit', router_ip]
    
    # Change to the script directory to ensure relative paths work
    script_dir = os.path.dirname(__file__)
    
    result = subprocess.run(command, capture_output=True, text=True, cwd=script_dir)
    result_output = result.stdout + result.stderr
    
    print("Ansible output:")
    print(result_output)
    
    if 'failed=0' in result_output and 'ok=' in result_output:
        pattern = os.path.join(script_dir, "show_run_66070136_*.txt")
        files = glob.glob(pattern)
        if files:
            return 'ok'
        else:
            return 'Error: Ansible - File not created'
    else:
        return 'Error: Ansible'
