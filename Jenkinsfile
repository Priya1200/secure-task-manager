pipeline {
    agent any

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
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}