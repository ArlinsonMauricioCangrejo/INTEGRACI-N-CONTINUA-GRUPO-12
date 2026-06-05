// =============================================================================
// Jenkinsfile - Sistema de Gestion de Tickets de Soporte
// Enfasis Profesional I (Integracion Continua) - Grupo 12
// Politecnico Grancolombiano
// =============================================================================
// Este pipeline declarativo define el flujo de integracion continua del
// proyecto. Se ejecuta automaticamente ante cada push en la rama main del
// repositorio en GitHub, y consta de los siguientes stages:
//
//   1. Checkout      - Descarga el codigo fuente desde GitHub
//   2. Build         - Construye las imagenes Docker del backend y frontend
//   3. Test          - Ejecuta la suite de 13 pruebas pytest en el backend
//   4. Deploy        - Levanta el stack completo con docker compose
//   5. Health Check  - Verifica que el sistema responde correctamente
//
// El bloque post define las acciones de notificacion segun el resultado
// del pipeline (exito o fallo).
// =============================================================================

pipeline {
    agent any

    environment {
        BUILD_TAG = "build-${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = '1'
        COMPOSE_PROJECT = 'ticket-system'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        // ---------------------------------------------------------------------
        // STAGE 1: Checkout - Descarga del codigo desde GitHub
        // ---------------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo "==> Descargando codigo desde GitHub (build ${env.BUILD_NUMBER})"
                checkout scm
                sh 'git log -1 --pretty=format:"Commit: %h - %s (%an)"'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 2: Build - Construccion de las imagenes Docker
        // ---------------------------------------------------------------------
        stage('Build') {
            steps {
                echo '==> Construyendo imagenes Docker del backend y frontend'
                sh 'docker compose -f docker-compose.yml build backend frontend'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 3: Test - Ejecucion de pruebas automatizadas pytest
        // ---------------------------------------------------------------------
        stage('Test') {
            steps {
                echo '==> Ejecutando suite de 13 pruebas pytest dentro del contenedor backend'
                sh '''
                    docker compose -f docker-compose.yml run --rm \\
                        -e DATABASE_URL=sqlite:///./test.db \\
                        backend pytest -v --tb=short
                '''
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 4: Deploy - Despliegue del stack completo
        // ---------------------------------------------------------------------
        stage('Deploy') {
            steps {
                echo '==> Desplegando stack completo en modo detached'
                sh 'docker compose -f docker-compose.yml up -d db backend frontend'
                sh 'sleep 5'
                sh 'docker compose -f docker-compose.yml ps'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 5: Health Check - Verificacion de salud del sistema
        // ---------------------------------------------------------------------
        stage('Health Check') {
            steps {
                echo '==> Verificando que el API responde correctamente'
                sh '''
                    for i in 1 2 3 4 5; do
                        if curl -sf http://backend:5000/api/health > /dev/null; then
                            echo "Backend respondiendo correctamente."
                            exit 0
                        fi
                        echo "Intento $i: backend aun no responde, esperando..."
                        sleep 3
                    done
                    echo "Backend no respondio despues de 5 intentos."
                    exit 1
                '''
            }
        }
    }

    // -------------------------------------------------------------------------
    // POST: Acciones segun el resultado del pipeline
    // -------------------------------------------------------------------------
    post {
        success {
            echo "Pipeline #${env.BUILD_NUMBER} ejecutado exitosamente."
            echo "Sistema desplegado y verificado en:"
            echo "   - Frontend:  http://localhost:8080"
            echo "   - Backend:   http://localhost:5000/api/health"
        }
        failure {
            echo "Pipeline #${env.BUILD_NUMBER} fallo. Revisar console output."
        }
        unstable {
            echo "Pipeline #${env.BUILD_NUMBER} inestable: algunas pruebas no pasaron."
        }
        always {
            echo "Build #${env.BUILD_NUMBER} finalizado en ${currentBuild.durationString}."
        }
    }
}
