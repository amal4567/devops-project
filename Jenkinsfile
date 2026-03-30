pipeline {
    agent any

    environment {
        IMAGE_NAME = "amalguerdani/flask-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_IMAGE = "${IMAGE_NAME}:${IMAGE_TAG}"
        DOCKER_IMAGE_LATEST = "${IMAGE_NAME}:latest"

        GITHUB_REPO_URL = "https://github.com/amal4567/devops-project.git"
        MASTER_IP = "15.188.233.85"

        K8S_DEPLOYMENT_FILE = "k8s\\app-deployment.yaml"
        K8S_SERVICE_FILE = "k8s\\app-service.yaml"
        K8S_DEPLOYMENT_NAME = "flask-app"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO_URL}"
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %DOCKER_IMAGE% -t %DOCKER_IMAGE_LATEST% .'
            }
        }

        stage('Test') {
    steps {
        bat 'docker run --rm -e PYTHONPATH=/app %DOCKER_IMAGE% pytest -v'    }
}
        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                bat 'docker push %DOCKER_IMAGE%'
                bat 'docker push %DOCKER_IMAGE_LATEST%'
            }
        }

        stage('Deploy to Kubernetes Master') {
    steps {
        withCredentials([sshUserPrivateKey(
            credentialsId: 'k8s-master-ssh',
            keyFileVariable: 'SSH_KEY',
            usernameVariable: 'SSH_USER'
        )]) {
            bat '''
            copy "%SSH_KEY%" "%WORKSPACE%\\jenkins_deploy_key" >nul
            icacls "%WORKSPACE%\\jenkins_deploy_key" /inheritance:r
            icacls "%WORKSPACE%\\jenkins_deploy_key" /grant:r "%USERNAME%:R" >nul

            scp -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no "%K8S_DEPLOYMENT_FILE%" %SSH_USER%@%MASTER_IP%:~/app-deployment.yaml
            scp -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no "%K8S_SERVICE_FILE%" %SSH_USER%@%MASTER_IP%:~/app-service.yaml

            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl apply -f ~/app-service.yaml --validate=false"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl apply -f ~/app-deployment.yaml --validate=false"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl set image deployment/%K8S_DEPLOYMENT_NAME% flask-app=%DOCKER_IMAGE%"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl rollout status deployment/%K8S_DEPLOYMENT_NAME% --timeout=180s"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl get deployment %K8S_DEPLOYMENT_NAME% -o=jsonpath='{.spec.template.spec.containers[0].image}'; echo"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl get pods -o wide"
            ssh -i "%WORKSPACE%\\jenkins_deploy_key" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo k3s kubectl get svc"

            del "%WORKSPACE%\\jenkins_deploy_key"
            '''
        }
    }
}
    }

    post {
        success {
            echo 'Pipeline SUCCESS: build, test, push, and deploy completed.'
        }
        failure {
            echo 'Pipeline FAILED: check the console output.'
        }
        always {
            bat 'docker image prune -f'
        }
    }
}