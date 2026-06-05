// =============================================================================
// Jenkinsfile - Sistema de Gestion de Tickets de Soporte
// Enfasis Profesional I (Integracion Continua) - Grupo 12
// Politecnico Grancolombiano
// =============================================================================

pipeline {
    agent any

    environment {
        BUILD_TAG = "build-${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = '1'
        COMPOSE_PROJECT_NAME = 'ticket-system-pipeline'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                echo "==> Descargando codigo desde GitHub (build ${env.BUILD_NUMBER})"
                checkout scm
                sh 'git log -1 --pretty=format:"Commit: %h - %s (%an)"'
            }
        }

        stage('Build') {
            steps {
                echo '==> Construyendo imagenes Docker del backend y frontend'
                sh 'docker compose -f docker-compose.yml build backend frontend'
            }
        }

        stage('Test') {
            steps {
                echo '==> Ejecutando pruebas pytest en instancia descartable del backend'
                sh '''
                    docker run --rm \
                        -e DATABASE_URL=sqlite:///./test.db \
                        ticket-system-pipeline-backend \
                        pytest -v --tb=short
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '==> Verificando el stack de produccion en ejecucion'
                sh '''
                    echo "Contenedores activos del proyecto:"
                    docker ps --filter "name=ticket-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '==> Verificando que el backend responde correctamente'
                sh '''
                    for i in 1 2 3 4 5; do
                        if curl -sf http://ticket-backend:5000/api/health > /dev/null; then
                            echo "Backend respondiendo correctamente en /api/health."
                            curl -s http://ticket-backend:5000/api/health
                            exit 0
                        fi
                        echo "Intento $i: backend aun no responde, esperando 3 segundos..."
                        sleep 3
                    done
                    echo "Backend no respondio despues de 5 intentos."
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline #${env.BUILD_NUMBER} ejecutado exitosamente."
            echo "Sistema verificado en:"
            echo "   - Frontend:  http://localhost:8080"
            echo "   - Backend:   http://localhost:5000/api/health"
        }
        failure {
            echo "Pipeline #${env.BUILD_NUMBER} fallo. Revisar console output."
        }
        always {
            echo "Build #${env.BUILD_NUMBER} finalizado en ${currentBuild.durationString}."
        }
    }
}
