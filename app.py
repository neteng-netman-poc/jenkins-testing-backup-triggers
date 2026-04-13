from flask import Flask, request, jsonify
from flask_cors import CORS
from helper_functions import return_info, backup_config, set_config, promote_beta_config
import requests as http_requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)

JENKINS_URL = 'https://jenkins.dheerajgajula.com'
JENKINS_JOB = 'jenkins-config-change-pipeline'
JENKINS_USER = 'admin'
with open("api-key.txt") as f:
    JENKINS_TOKEN = f.read().strip()


def trigger_jenkins_pipeline(ping_target='192.168.100.100', changed_hostname=''):
    try:
        resp = http_requests.post(
            f"{JENKINS_URL}/job/{JENKINS_JOB}/buildWithParameters",
            auth=HTTPBasicAuth(JENKINS_USER, JENKINS_TOKEN),
            params={'PING_TARGET': ping_target, 'CHANGED_HOSTNAME': changed_hostname}
        )
        return resp.status_code == 201
    except Exception:
        return False


@app.route("/config/<hostname>", methods=["POST"])
def receive_config(hostname: str):
    sshinfo_r = return_info(hostname)
    if sshinfo_r is None:
        return jsonify({"error": f"Hostname '{hostname}' not found"}), 404

    body = request.get_json(silent=True)
    if not body or "config" not in body:
        return jsonify({"error": "JSON body must contain a 'config' key"}), 400

    config = body["config"]

    backup_config(hostname)
    promote_beta_config(hostname)
    
    output = set_config(hostname, config)

    jenkins_triggered = trigger_jenkins_pipeline(changed_hostname=hostname)

    return jsonify({
        "status": "success",
        "hostname": hostname,
        "output": str(output),
        "jenkins_pipeline": "triggered" if jenkins_triggered else "trigger_failed"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
