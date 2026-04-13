"""
Jenkins stage script: Promote beta config for all routers.
Called only after all ping tests pass.
"""
import sys
import json
from helper_functions import promote_beta_config

with open("ip_hostname_mapping.json") as f:
    ip_map = json.load(f)

hostnames = list(ip_map.values())
failed = []

for hostname in hostnames:
    print(f"Promoting beta config for {hostname}...")
    try:
        promote_beta_config(hostname)
        print(f"[OK] {hostname}")
    except Exception as e:
        print(f"[ERROR] {hostname}: {e}")
        failed.append(hostname)

if failed:
    print(f"\n=== PROMOTE FAILED FOR: {', '.join(failed)} ===")
    sys.exit(1)

print("\n=== ALL BETA CONFIGS PROMOTED ===")
