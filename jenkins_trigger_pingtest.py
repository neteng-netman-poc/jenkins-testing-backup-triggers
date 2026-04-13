"""
Trigger the ping-test-pipeline on Jenkins from Python.

Usage: python jenkins_trigger_pingtest.py [PING_TARGET]
"""
import sys
import requests
from requests.auth import HTTPBasicAuth

JENKINS_URL = 'https://jenkins.dheerajgajula.com'
JOB_NAME = 'jenkins-config-change-pipeline'
USERNAME = 'admin'

with open("api-key.txt") as f:
    API_TOKEN = f.read().strip()

PING_TARGET = sys.argv[1] if len(sys.argv) > 1 else '192.168.100.100'


def trigger_ping_test():
    # buildWithParameters passes the PING_TARGET to the Jenkinsfile parameter
    trigger_url = f"{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters"
    print(f"Triggering pipeline: {trigger_url}")
    print(f"PING_TARGET = {PING_TARGET}")

    try:
        response = requests.post(
            trigger_url,
            auth=HTTPBasicAuth(USERNAME, API_TOKEN),
            params={'PING_TARGET': PING_TARGET}
        )

        if response.status_code == 201:
            print("Pipeline triggered successfully. Check Jenkins dashboard.")
        elif response.status_code == 400:
            # First run - parameters not yet registered. Use /build instead.
            print("Parameters not registered yet (first run). Triggering without parameters...")
            fallback_url = f"{JENKINS_URL}/job/{JOB_NAME}/build"
            response = requests.post(
                fallback_url,
                auth=HTTPBasicAuth(USERNAME, API_TOKEN)
            )
            if response.status_code == 201:
                print("Pipeline triggered (first run - uses default parameters).")
                print("Future runs will accept custom PING_TARGET.")
            else:
                print(f"Failed. HTTP {response.status_code}: {response.text}")
        else:
            print(f"Failed. HTTP {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")


if __name__ == '__main__':
    trigger_ping_test()
