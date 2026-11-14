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
                sh 'docker run --rm -v "$PWD/docker-practice":/src -w /src python:3.11-slim sh -c "pip install -q flask==3.1.3 pytest && python -m pytest -v tests"'
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
                sh 'echo "Build step placeholder"'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Applying Kubernetes manifests...'
                sh 'kubectl --kubeconfig=/var/lib/jenkins/.kube/config apply -f k8s/deployment.yaml'
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
