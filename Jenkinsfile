pipeline {
    agent any

    parameters {
        string(name: 'PING_TARGET', defaultValue: '192.168.100.100', description: 'IP address to ping from all routers')
        string(name: 'CHANGED_HOSTNAME', defaultValue: '', description: 'Hostname of the router whose config was changed')
    }

    environment {
        PYTHON_BIN = '/home/dheeraj/netman-finals-poc/venv/bin/python3'
        WORK_DIR   = '/home/dheeraj/netman-finals-poc/jenkins_tests'
    }

    stages {
        stage('Ping Test - All Routers') {
            steps {
                sh "cd ${WORK_DIR} && ${PYTHON_BIN} jenkins_ping_all.py ${params.PING_TARGET}"
            }
        }

        stage('Promote Beta Configs') {
            steps {
                sh "cd ${WORK_DIR} && ${PYTHON_BIN} jenkins_promote_all.py"
            }
        }
    }

    post {
        success {
            sh "cd ${WORK_DIR} && ${PYTHON_BIN} jenkins_send_notification.py success '${params.PING_TARGET}'"
        }
        failure {
            sh "cd ${WORK_DIR} && ${PYTHON_BIN} jenkins_rollback.py '${params.CHANGED_HOSTNAME}'"
            sh "cd ${WORK_DIR} && ${PYTHON_BIN} jenkins_send_notification.py failure '${params.PING_TARGET}' '${params.CHANGED_HOSTNAME}'"
        }
    }
}
