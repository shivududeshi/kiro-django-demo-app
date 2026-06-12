pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'django-demo-app'
        IMAGE_TAG      = 'latest'
        CONTAINER_NAME = 'django-demo-app'
        NETWORK        = 'petclinic-net'
        HOST_PORT      = '8000'
        CONTAINER_PORT = '8000'
    }

    stages {

        // ────────────────────────────────────────────────────────────
        // Stage 1 — Checkout source code
        // ────────────────────────────────────────────────────────────
        stage('get_code') {
            steps {
                checkout scm
            }
        }

        // ────────────────────────────────────────────────────────────
        // Stage 2 — Build Docker image
        // ────────────────────────────────────────────────────────────
        stage('build') {
            steps {
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        // ────────────────────────────────────────────────────────────
        // Stage 3 — Deploy container
        // ────────────────────────────────────────────────────────────
        stage('deploy') {
            steps {
                sh """
                    # Stop existing container if running
                    docker stop ${CONTAINER_NAME} || true

                    # Remove existing container if present
                    docker rm ${CONTAINER_NAME} || true

                    # Run new container on the existing petclinic-net network
                    docker run -d \\
                        --name ${CONTAINER_NAME} \\
                        --network ${NETWORK} \\
                        -p ${HOST_PORT}:${CONTAINER_PORT} \\
                        --env-file .env \\
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # Verify the container is up
                    docker ps --filter name=${CONTAINER_NAME}
                """
            }
        }
    }

    post {
        success {
            echo "Deployment successful — django-demo-app is running on port 8000"
        }
        failure {
            echo "Deployment failed — check the logs above"
        }
    }
}
