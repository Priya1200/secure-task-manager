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
                sh 'echo "Tests will go here"'
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
                sh 'echo "Build step placeholder"'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    echo "Simulating deployment process..."
                    echo "Copying build artifacts to deployment directory..."
                    mkdir -p deployment_output
                    echo "App deployed successfully at $(date)" > deployment_output/deploy_log.txt
                    cat deployment_output/deploy_log.txt
                '''
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