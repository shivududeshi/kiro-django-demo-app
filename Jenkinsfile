pipeline {
    agent { label 'petclinic-agent' }

    environment {
        GITHUB_REPO  = 'https://github.com/shivududeshi/kiro-django-demo-app'
        BRANCH       = 'master'
        APP_DIR      = '/var/www/kiro-django-demo-app'
        VENV_DIR     = "${APP_DIR}/envs"
        PYTHON       = '/usr/bin/python3.12'
        SERVICE_NAME = 'kiro-django-demo-app'
    }

    stages {

        // ── Stage 1: Get Code ────────────────────────────────────────────────
        stage('get_code') {
            steps {
                echo '>>> Checking out source code from GitHub...'
                git branch: "${BRANCH}",
                    url: "${GITHUB_REPO}"
                sh 'git log --oneline -3'
            }
        }

        // ── Stage 2: Build ───────────────────────────────────────────────────
        stage('build') {
            steps {
                echo '>>> Creating virtual environment...'
                sh """
                    if [ ! -d "${VENV_DIR}" ]; then
                        ${PYTHON} -m venv ${VENV_DIR}
                    fi
                    ${VENV_DIR}/bin/pip install --upgrade pip --quiet
                """

                echo '>>> Installing requirements...'
                sh """
                    ${VENV_DIR}/bin/pip install -r ${WORKSPACE}/requirements.txt --quiet
                """

                echo '>>> Running Django system check...'
                sh """
                    cd ${WORKSPACE}
                    ${VENV_DIR}/bin/python manage.py check
                """
            }
        }

        // ── Stage 3: Deploy ──────────────────────────────────────────────────
        stage('deploy') {
            steps {
                echo '>>> Deploying application...'
                sh """
                    chmod +x ${WORKSPACE}/deploy/deploy.sh
                    ${WORKSPACE}/deploy/deploy.sh
                """
            }
        }
    }

    post {
        success {
            echo '✅ Build SUCCESS — application is running on port 8000'
        }
        failure {
            echo '❌ Build FAILED — check the logs above'
        }
    }
}
