# Proyecto: Integración de TheHive, Cortex, MISP, Wazuh

## Descripción General

En este proyecto se va a desplegar una infraestructura de seguridad utilizando herramientas de código abierto como **Wazuh**, **TheHive**, **Cortex** y **MISP**. Estas herramientas permiten la monitorización de seguridad, la gestión de incidentes, el análisis de indicadores de compromiso (IOCs) y la inteligencia de amenazas.

Las herramientas a instalar y configurar son:
- **Wazuh**: Para monitorización de seguridad, detección de amenazas y análisis de logs.
- **TheHive**: Para la gestión de incidentes y casos de seguridad.
- **Cortex**: Para el análisis automático de observables e indicadores de compromiso (IOCs).
- **MISP**: Para la gestión y compartición de inteligencia de amenazas.

Con esta combinación, obtenemos **capacidades de seguridad de nivel profesional** que en productos comerciales costarían miles de dólares.

## Requisitos Previos

- **Docker** debe estar instalado en el sistema.
- Tener acceso a la terminal para ejecutar los comandos de Docker.

## Proceso de Instalación

### 1. Clonar el Repositorio de Wazuh para Docker

Primero, debemos clonar el repositorio de Wazuh para Docker desde GitHub para facilitar la instalación:

```bash
git clone https://github.com/wazuh/wazuh-docker.git
```

### 2. Luego de tenerlo clonado, hay que ubicarnos en la ubicación de los archivos en un cmd tradicional, y nos ubicamos dentro de la carpeta single node.
 
- ![Captura de pantalla](https://github.com/DavidJauregu123/Teoria_Informacion/blob/1e73ae77954e3e31851e0095899279791222bf40/Captura%20de%20pantalla%202025-09-18%20215826.png)


### 3. Ejecutar el Comando de Generación de Certificados, utilizando el siguiente comando:

```bash
docker-compose -f generate-indexer-certs.yml run --rm generator
```

- ![Captura de pantalla](https://github.com/DavidJauregu123/Teoria_Informacion/blob/b2918bb2113219cd786a6507d6261f604fa77e48/Captura%20de%20pantalla%202025-09-18%20220744.png)

### 4. Una vez generados los archivos, abre el archivo docker-compose.yml y reemplaza el contenido con el siguiente código de configuración:

```bash
services:

  # TheHive, MISP, Cortex Services

  thehive:
    container_name: thehive
    image: strangebee/thehive:5.2
    restart: unless-stopped
    depends_on:
      - cassandra
      - elasticsearch
      - minio
      - cortex
    mem_limit: 1500m
    ports:
      - "0.0.0.0:9000:9000"
    environment:
      - JVM_OPTS="-Xms1024M -Xmx1024M"
    command:
      - --secret
      - "lab123456789"
      - "--cql-hostnames"
      - "cassandra"
      - "--index-backend"
      - "elasticsearch"
      - "--es-hostnames"
      - "elasticsearch"
      - "--s3-endpoint"
      - "http://minio:9002"
      - "--s3-access-key"
      - "minioadmin"
      - "--s3-secret-key"
      - "minioadmin"
      - "--s3-use-path-access-style"
    volumes:
      - ./thehive/application.conf:/etc/thehive/application.conf
      - thehivedata:/opt/thehive/data
    networks:
      - SOC_NET

  cassandra:
    container_name: cassandra
    image: 'cassandra:4'
    restart: unless-stopped
    ports:
      - "0.0.0.0:9042:9042"
    environment:
      - CASSANDRA_CLUSTER_NAME=TheHive
    volumes:
      - cassandradata:/var/lib/cassandra
    networks:
      - SOC_NET

  elasticsearch:
    container_name: soc_elasticsearch
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.9
    restart: unless-stopped
    mem_limit: 512m
    ports:
      - "0.0.0.0:9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - cluster.name=hive
      - http.host=0.0.0.0
      - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
    volumes:
      - elasticsearchdata:/usr/share/elasticsearch/data
    networks:
      - SOC_NET

  minio:
    container_name: minio
    image: quay.io/minio/minio
    restart: unless-stopped
    command: ["minio", "server", "/data", "--console-address", ":9002"]
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    ports:
      - "0.0.0.0:9002:9002"
    volumes:
      - "miniodata:/data"
    networks:
      - SOC_NET

  cortex:
    container_name: cortex
    image: thehiveproject/cortex:latest
    restart: unless-stopped
    environment:
      - job_directory=/tmp/cortex-jobs
      - docker_job_directory=/tmp/cortex-jobs
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/cortex-jobs:/tmp/cortex-jobs
      - ./cortex/logs:/var/log/cortex
      - ./cortex/application.conf:/cortex/application.conf
    depends_on:
      - elasticsearch
    ports:
      - "0.0.0.0:9001:9001"
    networks:
      - SOC_NET

  misp:
    container_name: misp
    image: coolacid/misp-docker:core-latest
    restart: unless-stopped
    depends_on:
      - misp_mysql
    ports:
      - "0.0.0.0:80:80"
      - "0.0.0.0:443:443"
    volumes:
      - "./server-configs/:/var/www/MISP/app/Config/"
      - "./logs/:/var/www/MISP/app/tmp/logs/"
      - "./files/:/var/www/MISP/app/files"
      - "./ssl/:/etc/nginx/certs"
    environment:
      - MYSQL_HOST=misp_mysql
      - MYSQL_DATABASE=mispdb
      - MYSQL_USER=mispuser
      - MYSQL_PASSWORD=misppass
      - MISP_BASEURL=localhost
      - TIMEZONE=Europe/London
      - "INIT=true"
      - "CRON_USER_ID=1"
      - "REDIS_FQDN=redis"
      - "HOSTNAME=https://192.168.50.200" # Update to use your actual IP
    networks:
      - SOC_NET

  misp_mysql:
    container_name: misp_mysql
    image: mysql/mysql-server:5.7
    restart: unless-stopped
    volumes:
      - mispsqldata:/var/lib/mysql
    environment:
      - MYSQL_DATABASE=mispdb
      - MYSQL_USER=mispuser
      - MYSQL_PASSWORD=misppass
      - MYSQL_ROOT_PASSWORD=mispass
    networks:
      - SOC_NET

  redis:
    container_name: redis
    image: redis:latest
    hostname: redis
    networks:
      - SOC_NET

  misp-modules:
    container_name: misp_modules
    image: coolacid/misp-docker:modules-latest
    environment:
      - "REDIS_BACKEND=redis"
    depends_on:
      - redis
      - misp_mysql
    networks:
      - SOC_NET

  # Wazuh Services

  wazuh.manager:
    image: wazuh/wazuh-manager:4.11.0
    hostname: wazuh.manager
    restart: always
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 655360
        hard: 655360
    ports:
      - "1514:1514"
      - "1515:1515"
      - "514:514/udp"
      - "55000:55000"
    environment:
      - INDEXER_URL=https://wazuh.indexer:9200
      - INDEXER_USERNAME=admin
      - INDEXER_PASSWORD=SecretPassword
      - FILEBEAT_SSL_VERIFICATION_MODE=full
      - SSL_CERTIFICATE_AUTHORITIES=/etc/ssl/root-ca.pem
      - SSL_CERTIFICATE=/etc/ssl/filebeat.pem
      - SSL_KEY=/etc/ssl/filebeat.key
      - API_USERNAME=wazuh-wui
      - API_PASSWORD=MyS3cr37P450r.*-
    volumes:
      - wazuh_api_configuration:/var/ossec/api/configuration
      - wazuh_etc:/var/ossec/etc
      - wazuh_logs:/var/ossec/logs
      - wazuh_queue:/var/ossec/queue
      - wazuh_var_multigroups:/var/ossec/var/multigroups
      - wazuh_integrations:/var/ossec/integrations
      - wazuh_active_response:/var/ossec/active-response/bin
      - wazuh_agentless:/var/ossec/agentless
      - wazuh_wodles:/var/ossec/wodles
      - filebeat_etc:/etc/filebeat
      - filebeat_var:/var/lib/filebeat
      - ./config/wazuh_indexer_ssl_certs/root-ca-manager.pem:/etc/ssl/root-ca.pem
      - ./config/wazuh_indexer_ssl_certs/wazuh.manager.pem:/etc/ssl/filebeat.pem
      - ./config/wazuh_indexer_ssl_certs/wazuh.manager-key.pem:/etc/ssl/filebeat.key
      - ./config/wazuh_cluster/wazuh_manager.conf:/wazuh-config-mount/etc/ossec.conf
    networks:
      - SOC_NET

  wazuh.indexer:
    image: wazuh/wazuh-indexer:4.11.0
    hostname: wazuh.indexer
    restart: always
    ports:
      - "9201:9200" # Changed port to avoid conflict with ElasticSearch
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - wazuh-indexer-data:/var/lib/wazuh-indexer
      - ./config/wazuh_indexer_ssl_certs/root-ca.pem:/usr/share/wazuh-indexer/certs/root-ca.pem
      - ./config/wazuh_indexer_ssl_certs/wazuh.indexer-key.pem:/usr/share/wazuh-indexer/certs/wazuh.indexer.key
      - ./config/wazuh_indexer_ssl_certs/wazuh.indexer.pem:/usr/share/wazuh-indexer/certs/wazuh.indexer.pem
      - ./config/wazuh_indexer_ssl_certs/admin.pem:/usr/share/wazuh-indexer/certs/admin.pem
      - ./config/wazuh_indexer_ssl_certs/admin-key.pem:/usr/share/wazuh-indexer/certs/admin-key.pem
      - ./config/wazuh_indexer/wazuh.indexer.yml:/usr/share/wazuh-indexer/opensearch.yml
      - ./config/wazuh_indexer/internal_users.yml:/usr/share/wazuh-indexer/opensearch-security/internal_users.yml
    networks:
      - SOC_NET

  wazuh.dashboard:
    image: wazuh/wazuh-dashboard:4.11.0
    hostname: wazuh.dashboard
    restart: always
    ports:
      - "8443:5601" # Changed port to 8443 to avoid conflict with MISP
    environment:
      - INDEXER_USERNAME=admin
      - INDEXER_PASSWORD=SecretPassword
      - WAZUH_API_URL=https://wazuh.manager
      - DASHBOARD_USERNAME=kibanaserver
      - DASHBOARD_PASSWORD=kibanaserver
      - API_USERNAME=wazuh-wui
      - API_PASSWORD=MyS3cr37P450r.*-
    volumes:
      - ./config/wazuh_indexer_ssl_certs/wazuh.dashboard.pem:/usr/share/wazuh-dashboard/certs/wazuh-dashboard.pem
      - ./config/wazuh_indexer_ssl_certs/wazuh.dashboard-key.pem:/usr/share/wazuh-dashboard/certs/wazuh-dashboard-key.pem
      - ./config/wazuh_indexer_ssl_certs/root-ca.pem:/usr/share/wazuh-dashboard/certs/root-ca.pem
      - ./config/wazuh_dashboard/opensearch_dashboards.yml:/usr/share/wazuh-dashboard/config/opensearch_dashboards.yml
      - ./config/wazuh_dashboard/wazuh.yml:/usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml
      - wazuh-dashboard-config:/usr/share/wazuh-dashboard/data/wazuh/config
      - wazuh-dashboard-custom:/usr/share/wazuh-dashboard/plugins/wazuh/public/assets/custom
    depends_on:
      - wazuh.indexer
    networks:
      - SOC_NET

volumes:
  # TheHive/MISP/Cortex volumes
  miniodata:
  cassandradata:
  elasticsearchdata:
  thehivedata:
  mispsqldata:

  # Wazuh volumes
  wazuh_api_configuration:
  wazuh_etc:
  wazuh_logs:
  wazuh_queue:
  wazuh_var_multigroups:
  wazuh_integrations:
  wazuh_active_response:
  wazuh_agentless:
  wazuh_wodles:
  filebeat_etc:
  filebeat_var:
  wazuh-indexer-data:
  wazuh-dashboard-config:
  wazuh-dashboard-custom:

networks:
  SOC_NET:
    driver: bridge
```

### 4. Ejecuta el siguiente comando en la terminal de tu preferencia para crear la estructura de carpetas para Cortex y The Hive, así como los archivos de configuración:

- ![Captura de pantalla](https://github.com/DavidJauregu123/Teoria_Informacion/blob/b5a86195ea1fc36a86affdb5dc680c8b90322f5c/Captura%20de%20pantalla%202025-09-18%20221537.png)

### 5. En el documento de `application.conf` de cortex, el contenido se reemplaza con el lo siguiente:

```bash
    # Secret key
    play.http.secret.key="5jU6h1euT1jMJt3uCe3fbO2iGcoXOkF97XESPxkALivHblLd3vw8Vh4rJYpfL2wXcc"
    
    # HTTP configuration
    http.address=0.0.0.0
    http.port=9001
    
    # Akka configuration
    akka {
      cluster.enable = off
      actor {
        provider = local
      }
    }
    
    # ElasticSearch configuration
    search {
      index = cortex
      # Name of the index
      uri = "http://elasticsearch:9200/"
    }
    
    # Cache configuration
    cache.job = 10 minutes
    cache.user = 5 minutes
    cache.organization = 5 minutes
    
    job {
      runner = [docker]
    }
    
    # Docker job runner configuration
    dockerJobRunner {
      # Directory where job files are located
      directory = /tmp/cortex-jobs
      # Docker image timeout
      timeout = 30 minutes
      # Path to the docker executable
      dockerExecutable = "docker"
    }
    
    analyzer {
      config {
        # HTTP proxy configuration
        # proxy.host = proxy.example.com
        # proxy.port = 3128
        
        # HTTPS proxy configuration  
        # proxy.https.host = proxy.example.com
        # proxy.https.port = 3128
        
        # Proxy authentication
        # proxy.auth.username = username
        # proxy.auth.password = password
        
        # Ignore proxy for these hosts
        # proxy.nonProxyHosts = ["localhost", "127.0.0.1"]
      }
      
      # Analyzer timeouts
      timeout = 120 seconds
      
      # Fork join pool for analyzers
      fork-join-executor {
        parallelism-factor = 2.0
        parallelism-max = 4
      }
    }
    
    # Authentication configuration
    auth {
      provider = [local]
      
      # Multi-factor authentication
      multifactor = [totp]
      
      # Session timeout
      session.warning = 5m
      session.inactivity = 1h
    }
    
    # Datastore configuration
    datastore {
      name = data
      # Size of stored files
      chunksize = 1m
      hash {
        main = "SHA-256"
        extra = ["SHA-1", "MD5"]
      }
      attachment.password = "malware"
    }
    
    # Maximum textual content length
    play.http.parser.maxMemoryBuffer = 1M
    play.http.parser.maxDiskBuffer = 1G

```

### 6. Ya luego de tener todo eso, ya se puede levantar con el siguiente código:

```bash
`docker-compose up -d`
```

### 7. Luego de tener todo eso ya podemos meternos para comprobar que todo este bien:

- ![Captura de pantalla](https://github.com/DavidJauregu123/Teoria_Informacion/blob/94cc9d5d9e5e9ff8b6476777a92c368f48d02b9c/Captura%20de%20pantalla%202025-09-18%20222324.png)

### 8. Colaboramos que todas las paginas esten funcionando:

Wazuh Dashboard: https://<docker-host-ip>:8443

Login: admin | SecretPassword

MISP: https://<docker-host-ip>

Login: admin@admin.test | admin

The Hive: http://localhost:9000

Login: admin@thehive.local | secret

Cortex: http://localhost:9001

Login: admin | admin


