"""
Jenkins stage script: Rollback config for the changed router on pipeline failure.
Fetches the golden config from the API and restores it to the router.

Usage: python jenkins_rollback.py <CHANGED_HOSTNAME>
"""
import sys
from helper_functions import restore_config

CHANGED_HOSTNAME = sys.argv[1] if len(sys.argv) > 1 else ""

if not CHANGED_HOSTNAME:
    print("No hostname provided, skipping rollback.")
    sys.exit(0)

print(f"=== ROLLING BACK CONFIG FOR {CHANGED_HOSTNAME} ===")
try:
    restore_config(CHANGED_HOSTNAME)
    print(f"=== ROLLBACK SUCCESSFUL FOR {CHANGED_HOSTNAME} ===")
except Exception as e:
    print(f"=== ROLLBACK FAILED FOR {CHANGED_HOSTNAME}: {e} ===")
    sys.exit(1)
