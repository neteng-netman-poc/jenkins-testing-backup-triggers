"""
Jenkins stage script: SSH into all routers and ping a target IP.
Exits 0 if all routers report 100% success, exits 1 otherwise.

Usage: python jenkins_ping_all.py [PING_TARGET]
"""
import sys
import json
from helper_functions import return_info
from RunCommands import RunCommands

PING_TARGET = sys.argv[1] if len(sys.argv) > 1 else "192.168.100.100"

with open("ip_hostname_mapping.json") as f:
    ip_map = json.load(f)

hostnames = list(ip_map.values())
rc = RunCommands()
all_passed = True
failures = []

for hostname in hostnames:
    print(f"--- Pinging {PING_TARGET} from {hostname} ---")
    device_info = return_info(hostname=hostname)
    output = str(rc.single_device_single_command(device=device_info, command=f"ping {PING_TARGET}"))
    print(output)

    if "Success rate is 100 percent" in output:
        print(f"[PASS] {hostname}\n")
    else:
        print(f"[FAIL] {hostname}\n")
        all_passed = False
        failures.append(hostname)

if all_passed:
    print("=== ALL ROUTERS PASSED PING TEST ===")
    sys.exit(0)
else:
    print(f"=== FAILED ROUTERS: {', '.join(failures)} ===")
    sys.exit(1)
