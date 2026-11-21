pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'pip install -r requirements.txt || echo "No requirements.txt yet"'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh 'docker run --rm -v "$PWD/docker-practice":/src -w /src python:3.11-slim sh -c "pip install -q flask==3.1.3 pytest pytest-cov && python -m pytest -v tests --cov=app --cov-report=term-missing --cov-fail-under=80"'
            }
        }

        stage('Security Scan (DevSecOps)') {
            steps {
                echo 'Running security gate: dependency scan, SAST, secret scan, image scan...'
                sh 'bash security/scan.sh'
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                docker build -t sample-flask-app:1.0 docker-practice
                docker save sample-flask-app:1.0 | docker exec -i minikube ctr -n k8s.io images import -
                '''
            }
        }

        stage('Integration Tests (gate)') {
            steps {
                echo 'Starting the built image and running integration tests...'
                sh '''
                    docker rm -f it-app 2>/dev/null || true
                    docker network create itnet 2>/dev/null || true
                    docker run -d --name it-app --network itnet sample-flask-app:1.0
                    RC=0
                    docker run --rm --network itnet -e BASE_URL=http://it-app:5000 -v "$PWD/docker-practice":/src -w /src python:3.11-slim sh -c "pip install -q requests pytest && python -m pytest -v integration_tests" || RC=$?
                    docker rm -f it-app
                    exit $RC
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Applying Kubernetes manifests...'
                sh 'kubectl --kubeconfig=/var/lib/jenkins/.kube/config apply -f k8s/deployment.yaml'
                sh 'kubectl --kubeconfig=/var/lib/jenkins/.kube/config rollout restart deployment/flask-app-deployment'
                sh 'kubectl --kubeconfig=/var/lib/jenkins/.kube/config rollout status deployment/flask-app-deployment'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Application deployed.'
        }
        failure {
            echo 'Pipeline failed. Check logs above for details.'
        }
        always {
            echo "Build finished at ${new Date()}"
        }
    }
}
