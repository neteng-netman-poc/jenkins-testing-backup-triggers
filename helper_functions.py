from sshInfo import sshInfo
from RunCommands import RunCommands
import json
import requests


def getipHostname(hostname: str):
    with open("ip_hostname_mapping.json") as f:
        ip_map = json.load(f)
    ip = next(ip for ip, name in ip_map.items() if name == hostname)
    return ip

def return_sshinfo(sshinfo: tuple, ip: str):
    for info in sshinfo:
        if info.get("ip") == ip:
            return info
    return None

def return_info(hostname: str):
    sinfo = sshInfo(config_file="sshInfo.csv")
    sshinfo = sinfo.return_sshconfigs()
    ip = getipHostname(hostname=hostname)
    sshinfo_r = return_sshinfo(sshinfo=sshinfo[0], ip=ip)
    return sshinfo_r

def backup_config(hostname: str):
    device_info = return_info(hostname=hostname)
    rc = RunCommands()
    running_config_lines = rc.get_running_config(device=device_info)
    if isinstance(running_config_lines, str):
        raise Exception(f"Failed to get config from {hostname}: {running_config_lines}")
    backed_up_config = "\n".join(running_config_lines)
    management_ip = device_info.get("ip")

    url = "https://api-netman.dheerajgajula.com/api/config/push-beta"
    payload = json.dumps({
        "router_hostname": hostname,
        "router_management_ip": management_ip,
        "backed_up_config": backed_up_config
    })
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.text


def set_config(hostname: str, config):
    device_info = return_info(hostname=hostname)
    if isinstance(config, str):
        config = config.splitlines()
    rc = RunCommands()
    output = rc._set_config_single_device(device=device_info, commands=config)
    return output

def fetch_golden_config(hostname: str):
    url = f"https://api-netman.dheerajgajula.com/api/config/all?router_hostname={hostname}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    golden_configs = data["configs"]["golden_running_configs"]
    return golden_configs["backed_up_config"]


def restore_config(hostname: str):
    config = fetch_golden_config(hostname)
    print(f"Restoring golden config to {hostname}...")
    output = set_config(hostname, config)
    print(f"Config restored to {hostname} successfully.")
    return output


def promote_beta_config(hostname: str):
    url = "https://api-netman.dheerajgajula.com/api/config/promote-beta"

    payload = json.dumps({
    "router_hostname": hostname
    })
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def promote_golden_config(hostname: str):
    url = "https://api-netman.dheerajgajula.com/api/config/promote-golden"

    payload = json.dumps({
        "router_hostname": hostname
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def populate_golden_configs():
    """
    Populate golden configs for all routers.
    Steps:
      1. Pull running config from each router and push to beta (push-beta)
      2. Promote beta to golden_running (promote-beta)
      3. Promote golden_running to golden (promote-golden)
    """
    with open("ip_hostname_mapping.json") as f:
        ip_map = json.load(f)

    hostnames = list(ip_map.values())
    failed = []

    for hostname in hostnames:
        try:
            print(f" Backing up running config for {hostname} (push-beta)...")
            result = backup_config(hostname)
            print(f"[OK] push-beta: {result}")

            print(f" Promoting beta config for {hostname} (promote-beta)...")
            promote_beta_config(hostname)

            print(f" Promoting to golden config for {hostname} (promote-golden)...")
            promote_golden_config(hostname)

            print(f"[OK] {hostname} golden config populated.\n")
        except Exception as e:
            print(f"[ERROR] {hostname}: {e}")
            failed.append(hostname)

    if failed:
        print(f"\n=== GOLDEN POPULATE FAILED FOR: {', '.join(failed)} ===")
    else:
        print(f"\n=== ALL GOLDEN CONFIGS POPULATED FOR COLLECTION: ===")

    return failed

