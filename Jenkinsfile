pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }

    stages {
        stage('Install') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest -v'
            }
        }
    }
}