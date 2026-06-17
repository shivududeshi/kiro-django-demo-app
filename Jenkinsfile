pipeline {

    agent { label 'test-nodenote' }

    environment {
        IMAGE_NAME     = 'django-demo-app'
        IMAGE_TAG      = 'latest'
        CONTAINER_NAME = 'django-demo-app'
        NETWORK        = 'django-net'
        HOST_PORT      = '8000'
        CONTAINER_PORT = '8000'
        REPO_URL       = 'https://github.com/shivududeshi/kiro-django-demo-app.git'
        BRANCH         = 'main'
    }

    triggers {
        githubPush()  // fires on every push — no SCM polling
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ────────────────────────────────────────────
        // Stage 1 — Checkout source code
        // ────────────────────────────────────────────
        stage('get_code') {
            steps {
                git branch: "${BRANCH}", url: "${REPO_URL}"
            }
        }

        // ────────────────────────────────────────────
        // Stage 2 — Build Docker image
        // ────────────────────────────────────────────
        stage('build') {
            steps {
                sh """
                    docker build \\
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \\
                        -f Dockerfile \\
                        .
                """
            }
        }

        // ────────────────────────────────────────────
        // Stage 3 — Deploy container on target server
        // ────────────────────────────────────────────
        stage('deploy') {
            steps {
                // Stop and remove existing container if present
                sh 'docker stop ${CONTAINER_NAME} 2>/dev/null || true'
                sh 'docker rm   ${CONTAINER_NAME} 2>/dev/null || true'

                // Ensure docker network exists
                sh 'docker network inspect ${NETWORK} >/dev/null 2>&1 || docker network create ${NETWORK}'

                // ── Start MySQL if not already running ──────────────────────
                sh """
                    if docker ps --format "{{.Names}}" | grep -q "^mysql\$"; then
                        echo "MySQL container already running — skipping start"
                    else
                        docker stop mysql 2>/dev/null || true
                        docker rm   mysql 2>/dev/null || true
                        docker run -d \\
                            --name mysql \\
                            --network ${NETWORK} \\
                            -e MYSQL_ROOT_PASSWORD=rootpassword \\
                            -e MYSQL_DATABASE=world \\
                            -e MYSQL_USER=petclinic \\
                            -e MYSQL_PASSWORD=petclinic \\
                            --restart unless-stopped \\
                            mysql:8.0
                        echo "Waiting for MySQL to be ready..."
                        for i in \$(seq 1 24); do
                            docker exec mysql mysqladmin ping -h localhost -u root --password=rootpassword --silent 2>/dev/null \\
                                && echo "MySQL is ready" && break
                            echo "  Attempt \$i — MySQL not ready yet..."
                            sleep 5
                        done
                    fi
                """

                // ── Load world database schema + data if tables don't exist ──
                sh """
                    # Extra wait: mysqladmin ping passes before grant tables are fully ready
                    echo "Waiting 5s for MySQL auth to stabilise..."
                    sleep 5

                    # Retry the table check up to 5 times in case auth is still warming up
                    TABLE_EXISTS="0"
                    for i in \$(seq 1 5); do
                        RESULT=\$(docker exec mysql mysql -u root --password=rootpassword \
                            --skip-column-names -e \
                            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='world' AND table_name='city';" \
                            2>/dev/null)
                        if [ \$? -eq 0 ]; then
                            TABLE_EXISTS="\${RESULT:-0}"
                            break
                        fi
                        echo "  Auth not ready yet (attempt \$i) — retrying in 5s..."
                        sleep 5
                    done

                    if [ "\$TABLE_EXISTS" = "0" ] || [ "\$TABLE_EXISTS" = "" ]; then
                        echo "Loading world.sql into MySQL..."
                        docker exec -i mysql mysql -u root --password=rootpassword world < world.sql
                        echo "world.sql loaded successfully"
                    else
                        echo "Tables already exist (count=\$TABLE_EXISTS) — skipping SQL import"
                    fi
                """

                // Write .env file for the container
                sh '''
                    cat > /tmp/django-demo.env <<EOF
DJANGO_SECRET_KEY=3xb%+*2uex+%1&\$@=*+(@^atnm!#tz-n&i5qn\$o46jnp&u*2l^
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=* 0.0.0.0 localhost 13.232.24.60
DB_NAME=world
DB_USER=petclinic
DB_PASSWORD=petclinic
DB_HOST=mysql
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=shivas.shiva01012000@gmail.com
EMAIL_HOST_PASSWORD=lbfs camj axvt akdj
EOF
                '''

                // Run new container joining django-net
                sh """
                    docker run -d \\
                        --name ${CONTAINER_NAME} \\
                        --network ${NETWORK} \\
                        -p ${HOST_PORT}:${CONTAINER_PORT} \\
                        --env-file /tmp/django-demo.env \\
                        --restart unless-stopped \\
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """

                // Run Django migrations (creates django_session, auth tables, etc.)
                sh 'docker exec ${CONTAINER_NAME} python manage.py migrate --noinput'

                // Rebuild Whoosh search index so search returns results
                sh 'docker exec ${CONTAINER_NAME} python manage.py rebuild_index --noinput'

                // Health check — wait up to 90s for /health to return 200
                sh '''
                    echo "Waiting for django-demo-app to be healthy..."
                    for i in $(seq 1 18); do
                        STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                                 http://localhost:8000/health || echo "000")
                        echo "  Attempt $i — HTTP $STATUS"
                        [ "$STATUS" = "200" ] && echo "Health check PASSED" && exit 0
                        sleep 5
                    done
                    echo "ERROR: App did not become healthy in 90s"
                    docker logs --tail 50 ${CONTAINER_NAME}
                    exit 1
                '''

                // Confirm container is running
                sh 'docker ps --filter name=${CONTAINER_NAME}'
            }
            post {
                failure {
                    sh 'docker logs --tail 100 ${CONTAINER_NAME} || true'
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS — django-demo-app is live on port 8000"
        }
        failure {
            echo "Pipeline FAILED — check stage logs above"
        }
    }
}
