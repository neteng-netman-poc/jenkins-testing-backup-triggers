"""
Jenkins stage script: Send success or failure email notification.

Usage:
  Config pipeline: python jenkins_send_notification.py <success|failure> <PING_TARGET> [CHANGED_HOSTNAME]
  Nightly backup:  python jenkins_send_notification.py <success|failure> nightly
"""
import sys
import json
import requests

STATUS = sys.argv[1] if len(sys.argv) > 1 else "success"
PING_TARGET = sys.argv[2] if len(sys.argv) > 2 else "192.168.100.100"
CHANGED_HOSTNAME = sys.argv[3] if len(sys.argv) > 3 else ""

EMAIL_API_URL = "https://email.dheerajgajula.com/send-custom"
TARGET_EMAIL = "dheeraj.cuboulder@gmail.com"

with open("ip_hostname_mapping.json") as f:
    ip_map = json.load(f)

hostnames = list(ip_map.values())
router_list = ", ".join(hostnames)

if PING_TARGET == "nightly":
    if STATUS == "success":
        subject = "Nightly Backup PASSED - All Configs Backed Up"
        content = (
            f"Nightly backup completed successfully.\n"
            f"Routers backed up: {router_list}"
        )
    else:
        subject = "Nightly Backup FAILED - Action Required"
        content = (
            f"Nightly backup failed for one or more routers.\n"
            f"Routers: {router_list}\n"
            f"Check Jenkins logs for details."
        )
elif STATUS == "success":
    subject = "Jenkins Pipeline PASSED - Beta Configs Promoted"
    content = (
        f"All routers ({router_list}) successfully pinged {PING_TARGET}.\n"
        f"Beta configurations have been promoted to production."
    )
else:
    subject = "Jenkins Pipeline FAILED - Config Rolled Back"
    rollback_msg = (
        f"The golden config for {CHANGED_HOSTNAME} has been restored automatically."
        if CHANGED_HOSTNAME
        else "No specific router was targeted for rollback."
    )
    content = (
        f"The ping test pipeline failed for target {PING_TARGET}.\n"
        f"Routers tested: {router_list}\n"
        f"Beta config promotion was skipped.\n\n"
        f"Rollback: {rollback_msg}\n"
        f"Check Jenkins logs for details."
    )

payload = json.dumps({
    "target_email": TARGET_EMAIL,
    "subject": subject,
    "content": content
})

print(f"Sending {STATUS} notification to {TARGET_EMAIL}")
response = requests.post(
    EMAIL_API_URL,
    headers={"Content-Type": "application/json"},
    data=payload
)

print(f"Response: {response.status_code} - {response.text}")
