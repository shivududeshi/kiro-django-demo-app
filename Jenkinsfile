pipeline {
    agent any

    environment {
        GITHUB_REPO     = 'https://github.com/shivududeshi/kiro-django-demo-app'
        BRANCH          = 'master'
        APP_DIR         = '/var/www/kiro-django-demo-app'
        PYTHON          = '/usr/bin/python3.12'
        VENV_DIR        = "${APP_DIR}/envs"
        DEPLOY_USER     = 'ubuntu'
        DEPLOY_HOST     = 'localhost'   // same node — Jenkins agent IS the server
    }

    stages {

        // ── Stage 1: Get Code ────────────────────────────────────────────────
        stage('Get Code') {
            steps {
                echo '>>> Checking out source code from GitHub...'
                git branch: "${BRANCH}",
                    url: "${GITHUB_REPO}"
                echo ">>> Checked out branch: ${BRANCH}"
                sh 'git log --oneline -5'
            }
        }

        // ── Stage 2: Build ───────────────────────────────────────────────────
        stage('Build') {
            steps {
                echo '>>> Setting up Python virtualenv and installing dependencies...'
                sh """
                    # Create virtualenv if it does not exist
                    if [ ! -d "${VENV_DIR}" ]; then
                        ${PYTHON} -m venv ${VENV_DIR}
                    fi

                    # Upgrade pip
                    ${VENV_DIR}/bin/pip install --upgrade pip

                    # Install all dependencies
                    ${VENV_DIR}/bin/pip install -r ${WORKSPACE}/requirements.txt

                    echo '>>> Dependencies installed successfully'
                    ${VENV_DIR}/bin/pip list
                """

                echo '>>> Running Django system check...'
                sh """
                    export DJANGO_SETTINGS_MODULE=panorbit.settings
                    export PYTHONPATH=${WORKSPACE}
                    cd ${APP_DIR}
                    ${VENV_DIR}/bin/python manage.py check
                """

                echo '>>> Running tests...'
                sh """
                    cd ${APP_DIR}
                    ${VENV_DIR}/bin/python manage.py test world --verbosity=2 || true
                """
            }
        }

        // ── Stage 3: Deploy ──────────────────────────────────────────────────
        stage('Deploy') {
            steps {
                echo '>>> Deploying application...'
                sh """
                    chmod +x ${WORKSPACE}/deploy/deploy.sh
                    ${WORKSPACE}/deploy/deploy.sh
                """
            }
        }
    }

    // ── Post actions ─────────────────────────────────────────────────────────
    post {
        success {
            echo '✅ Pipeline completed successfully. App is live at http://13.201.40.146'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above for details.'
        }
        always {
            echo '>>> Pipeline finished.'
        }
    }
}
