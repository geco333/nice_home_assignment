pipeline {
    agent any

    // In dev/staging/production runs all environment variables are exported from
    // a dedicated configuration file reterived from remote storage.
    environment {
        BASE_URL         = 'https://parabank.parasoft.com/parabank'
        API_BASE_URL     = 'https://parabank.parasoft.com/parabank/services/bank'
        HEADLESS         = 'true'
        SLOW_MO          = '0'
        TIMEOUT          = '30000'
        REGISTRY         = "${params.DOCKER_REGISTRY ?: 'docker.io/myorg'}"
        IMAGE_NAME       = 'parabank-tests'
        IMAGE_TAG        = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.take(7) ?: 'latest'}"
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'The environment to run the tests in')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    python -m playwright install --with-deps chromium
                '''
            }
        }
        stage('Run Negative Tests') {
            steps {
                sh 'pytest tests/negative/ -m negative'
            }
        }
        stage("Run E2E Tests") {
            steps {
                sh 'pytest tests/e2e/ -m e2e'
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"

                // Credentials discovery depends on the jenkins credentials plugin.
                withCredentials([usernamePassword(
                    credentialsId: 'DOCKER_REGISTRY_CREDS',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login $REGISTRY -u $DOCKER_USER --password-stdin'
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                }
            }
        }
    }

    post {
        always {
            // Publish allure report.
            allure includeProperties: false,
                   results: [[path: 'reports/allure-results']]

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
        failure {
            echo 'Tests failed — check the Allure report for details.'
        }
        cleanup {
            sh "docker rmi ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} || true"
            sh "docker rmi ${REGISTRY}/${IMAGE_NAME}:latest || true"
            sh 'docker logout $REGISTRY || true'
        }
    }
}
