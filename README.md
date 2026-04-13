# Jenkins Network Automation Tests

CI/CD pipelines and automation scripts for managing Cisco router configurations via Jenkins. Part of the **NetMan** network management system.

## Overview

This repo provides two Jenkins pipelines that automate configuration management across a fleet of routers (R1-R5):

1. **Config Change Pipeline** (`Jenkinsfile`) -- Triggered via the Flask API whenever a router config is pushed. Runs ping tests across all routers, promotes beta configs on success, or rolls back the changed router on failure.
2. **Nightly Backup Pipeline** (`Jenkinsfile_nightly`) -- Runs on a daily cron (`0 0 * * *`). SSHes into every router, pulls the running config, and pushes it to the nightly backup API.

Both pipelines send email notifications on success or failure.

## Architecture

```
User pushes config via API
        |
        v
  app.py (Flask, port 5001)
        |
        |-- Backs up current running config (SSH + API)
        |-- Promotes beta config via API
        |-- Applies new config to router (SSH/Netmiko)
        |-- Triggers Jenkins pipeline
                |
                v
        Jenkinsfile pipeline
          1. Ping all routers -> target IP
          2. If pass: promote beta configs for all routers
          3. If fail: rollback changed router to golden config
          4. Send email notification
```

## File Descriptions

| File | Description |
|------|-------------|
| `app.py` | Flask API server. Accepts config pushes at `POST /config/<hostname>`, applies them, and triggers Jenkins. |
| `Jenkinsfile` | Config change pipeline -- ping test, promote, rollback on failure. |
| `Jenkinsfile_nightly` | Nightly backup pipeline -- backs up all router configs on a daily schedule. |
| `RunCommands.py` | Netmiko wrapper for SSH command execution and config management on Cisco devices. |
| `helper_functions.py` | Shared utilities: device lookup, config backup/restore, golden config fetch, beta promotion. |
| `sshInfo.py` | Reads SSH connection details (IP, credentials, device type) from `sshInfo.csv`. |
| `jenkins_ping_all.py` | Pings a target IP from every router. Exits non-zero if any router fails. |
| `jenkins_promote_all.py` | Promotes beta config to production for all routers. |
| `jenkins_rollback.py` | Restores the golden config on a specific router after a failed pipeline. |
| `jenkins_nightly_backup.py` | Backs up running configs for all routers to the nightly backup API. |
| `jenkins_send_notification.py` | Sends success/failure email notifications for both pipelines. |
| `jenkins_trigger_pingtest.py` | Standalone script to trigger the Jenkins pipeline from the command line. |
| `jenkins_pingtest.py` | Single-router ping test (used for ad-hoc testing). |
| `ip_hostname_mapping.json` | Maps management IPs to router hostnames (R1-R5). |
| `sshInfo.csv` | SSH connection parameters for each router (IP, username, password, device type, enable secret). |
| `error_codes.env` | Custom error codes used by `sshInfo.py`. |
| `api-key.txt` | Jenkins API token (not committed). |

## Prerequisites

- Python 3.x
- Jenkins instance with pipeline support
- Network access to managed routers via SSH
- Access to the NetMan API (`api-netman.dheerajgajula.com`)

### Python Dependencies

- `flask`
- `flask-cors`
- `netmiko`
- `pandas`
- `python-dotenv`
- `requests`

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd jenkins_tests
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask flask-cors netmiko pandas python-dotenv requests
   ```

3. Add your Jenkins API token:
   ```bash
   echo "your-jenkins-api-token" > api-key.txt
   ```

4. Ensure `sshInfo.csv` contains correct SSH credentials for your routers.

5. Update `ip_hostname_mapping.json` to match your network topology.

6. Configure the two Jenkins pipelines pointing to `Jenkinsfile` and `Jenkinsfile_nightly`. Update the `PYTHON_BIN` and `WORK_DIR` environment variables in each Jenkinsfile to match your setup.

## Usage

### Start the Flask API server

```bash
python app.py
```

The server runs on port 5001. Push a config to a router:

```bash
curl -X POST http://localhost:5001/config/R1 \
  -H "Content-Type: application/json" \
  -d '{"config": "interface Loopback0\n ip address 10.0.0.1 255.255.255.0"}'
```

### Trigger the Jenkins pipeline manually

```bash
python jenkins_trigger_pingtest.py [PING_TARGET]
```

### Run a ping test from all routers

```bash
python jenkins_ping_all.py 192.168.100.100
```
