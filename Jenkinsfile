pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONDONTWRITEBYTECODE = '1'
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
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -U pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v \
                        --tb=short \
                        --cov=app \
                        --cov=db \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov \
                        --junit-xml=pytest.xml
                '''
            }
        }

        stage('Publish coverage') {
            steps {
                publishHTML(target: [
                    allowMissing:         false,
                    alwaysLinkToLastBuild: true,
                    keepAll:              true,
                    reportDir:            'htmlcov',
                    reportFiles:          'index.html',
                    reportName:           'Coverage Report'
                ])
            }
        }
    }

    post {
        always {
            // Test results
            junit allowEmptyResults: true, testResults: 'pytest.xml'

            // Coverage artifact
            archiveArtifacts artifacts: 'htmlcov/**,coverage.xml',
                             allowEmptyArchive: true
        }

        success {
            echo "✅ All tests passed."
        }

        failure {
            echo "❌ Tests failed — check the report above."
        }
    }
}