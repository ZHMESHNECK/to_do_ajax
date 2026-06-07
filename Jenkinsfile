pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup venv') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/Scripts/activate || source venv/bin/activate
                    pip install -U pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    . venv/Scripts/activate || source venv/bin/activate
                    pytest -v --tb=short --cov=app --cov-report=xml --cov-report=html
                '''
            }
        }

        stage('Publish coverage') {
            steps {
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
            junit 'pytest.xml'
        }
    }
}