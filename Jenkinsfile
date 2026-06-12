// =============================================================================
// Jenkinsfile - Sistema de Gestion de Tickets de Soporte
// Enfasis Profesional I (Integracion Continua) - Grupo 12
// Politecnico Grancolombiano
// =============================================================================
// Pipeline de Integracion y Despliegue Continuo.
//
// A diferencia de la version inicial (que solo construia y verificaba), este
// pipeline TAMBIEN despliega: tras construir y probar, recrea los contenedores
// de produccion (frontend y backend) para que los cambios queden visibles de
// inmediato en http://localhost:8080. Esto evidencia el ciclo CI/CD completo:
// push -> build -> test -> deploy -> health check.
//
// NOTA: el pipeline opera sobre el MISMO proyecto Docker Compose que el stack
// de produccion ('ticket-system'), de modo que recrea los contenedores reales
// y no una copia paralela. El servicio 'jenkins' y la base de datos 'db' NUNCA
// se incluyen en el despliegue, para no reiniciar a Jenkins durante su propia
// corrida ni recrear la base de datos.
// =============================================================================

pipeline {
    agent any

    environment {
        BUILD_TAG = "build-${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = '1'
        // Debe coincidir con el nombre de proyecto del stack de produccion en
        // el host (la carpeta 'ticket-system'). Asi Jenkins recrea los
        // contenedores reales y no unos en un proyecto aparte.
        COMPOSE_PROJECT_NAME = 'ticket-system'
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
                        ticket-system-backend \
                        pytest -v --tb=short
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '==> Desplegando: reconstruye y recrea frontend y backend en produccion'
                sh '''
                    # Recrea SOLO frontend y backend dentro del proyecto ticket-system.
                    # No se incluye 'jenkins' (se mataria a si mismo) ni 'db'
                    # (para preservar los datos). El --build garantiza que el
                    # contenedor quede con la ultima version del codigo.
                    docker compose -f docker-compose.yml up -d --build frontend backend

                    echo "Contenedores activos del proyecto:"
                    docker ps --filter "name=ticket-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '==> Verificando que el backend recien desplegado responde correctamente'
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
            echo "Pipeline #${env.BUILD_NUMBER} ejecutado y desplegado exitosamente."
            echo "Sistema actualizado y verificado en:"
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
