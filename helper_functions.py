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
    


