pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "amalguerdani/flask-app:latest"
        GITHUB_REPO_URL = "https://github.com/amal4567/devops-project.git"
        MASTER_IP = "15.188.233.85"
        K8S_DEPLOYMENT_FILE = "k8s\\app-deployment.yaml"
        K8S_SERVICE_FILE = "k8s\\app-service.yaml"
        K8S_DEPLOYMENT_NAME = "flask-app"
    }

    stages {
        stage('Build Docker') {
            steps {
                bat 'docker build -t %DOCKER_IMAGE% .'
            }
        }

        stage('Login Docker') {
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

        stage('Push Image') {
            steps {
                bat 'docker push %DOCKER_IMAGE%'
            }
        }

        stage('Deploy to Kubernetes Master') {
           steps {
            withCredentials([sshUserPrivateKey(
                credentialsId: 'k8s-master-ssh',
                keyFileVariable: 'SSH_KEY',
                usernameVariable: 'SSH_USER'
            )]) {
                bat """
                scp -i "%SSH_KEY%" -o StrictHostKeyChecking=no %K8S_DEPLOYMENT_FILE% %SSH_USER%@%MASTER_IP%:~/app-deployment.yaml
                scp -i "%SSH_KEY%" -o StrictHostKeyChecking=no %K8S_SERVICE_FILE% %SSH_USER%@%MASTER_IP%:~/app-service.yaml

                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl apply -f ~/app-deployment.yaml"
                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl apply -f ~/app-service.yaml"
                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl rollout restart deployment/%K8S_DEPLOYMENT_NAME%"
                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl rollout status deployment/%K8S_DEPLOYMENT_NAME% --timeout=180s"
                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl get pods"
                ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no %SSH_USER%@%MASTER_IP% "sudo kubectl get svc"
                """
            }
        }
    }
    }

    post {
        success {
            echo 'Pipeline SUCCESS: build, push, and deploy completed.'
        }
        failure {
            echo 'Pipeline FAILED: check the console output.'
        }
    }
}