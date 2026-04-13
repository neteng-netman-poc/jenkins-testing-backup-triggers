"""
Jenkins stage script: Nightly backup of running configs for all routers.
SSHes into each router, grabs the running config, and pushes it to the nightly-backup API.

Usage: python jenkins_nightly_backup.py
"""
import sys
import json
import requests
from helper_functions import return_info
from RunCommands import RunCommands

NIGHTLY_BACKUP_URL = "https://api-netman.dheerajgajula.com/api/config/nightly-backup"

with open("ip_hostname_mapping.json") as f:
    ip_map = json.load(f)

hostnames = list(ip_map.values())
rc = RunCommands()
failed = []

for hostname in hostnames:
    print(f"--- Backing up {hostname} ---")
    try:
        device_info = return_info(hostname=hostname)
        management_ip = device_info.get("ip")

        running_config_lines = rc.get_running_config(device=device_info)
        if isinstance(running_config_lines, str):
            raise Exception(f"Failed to get config from {hostname}: {running_config_lines}")
        backed_up_config = "\n".join(running_config_lines)

        payload = json.dumps({
            "router_hostname": hostname,
            "router_management_ip": management_ip,
            "backed_up_config": backed_up_config
        })
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.post(NIGHTLY_BACKUP_URL, headers=headers, data=payload)
        print(f"[OK] {hostname} - API response: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {hostname}: {e}")
        failed.append(hostname)

if failed:
    print(f"\n=== NIGHTLY BACKUP FAILED FOR: {', '.join(failed)} ===")
    sys.exit(1)

print("\n=== NIGHTLY BACKUP COMPLETE FOR ALL ROUTERS ===")
