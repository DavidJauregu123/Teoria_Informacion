# Tarea #997 Proyecto the hive + cortex + MISP + Wazuh

## ¿Qué vamos a construir?

- **Wazuh (despliegue de un solo nodo):** para monitorización de seguridad, detección de amenazas y análisis de logs.  
- **TheHive:** para la gestión de incidentes y casos de seguridad.  
- **Cortex:** para el análisis automático de observables e indicadores de compromiso (IOCs).  
- **MISP:** para la gestión y compartición de inteligencia de amenazas.  

---

Con esta combinación, obtienes **capacidades de seguridad de nivel profesional** que en productos comerciales costarían miles de dólares.


### Empezar con el proyecto

Se debe tener instalado lo que es docker.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/513d3142-f097-4ce2-bf22-36d20009bd36" />

Teniendo encuenta esto ahora hay que tener clonado el repositor de github de Wazuh para docker, este nos facilita la instalación. 

Este es el repositorio que utilice: https://github.com/wazuh/wazuh-docker?tab=readme-ov-file

`git clone https://github.com/wazuh/wazuh-docker.git`

Luego de tenerlo clonado, hay que ubicarnos en la ubicación de los archivos en un cmd tradicional

<img width="346" height="56" alt="image" src="https://github.com/user-attachments/assets/94979381-3f67-499d-9891-6ed3ab766ff8" />

Luego de ubicarse en la dirección ejecutar el siguiente código para empezar a construir el docker:

`docker-compose -f generate-indexer-certs.yml run --rm generator`

<img width="1920" height="1080" alt="Captura de pantalla (864)" src="https://github.com/user-attachments/assets/ba3f9787-84fe-49a0-9550-46b78026e729" />

Se comienza a generar archivos como el docker-compose.yml, que es la siguiente a modificar.

Se abre el archivo de docker-compose.yml y se reemplaza todo con el siguiente código:


    
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
      

Luego de tener esto, se debe crear los las siguientes carpetas y archivos:
    
    mkdir cortex thehive
    type nul > cortex\application.conf
    type nul > thehive\application.conf


Donde en el documento de `application.conf` de cortex, el contenido se reemplaza con el lo siguiente:
    
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


Ya luego de tener todo eso, ya se puede levantar con el siguiente código:

`docker-compose up -d`

Luego de tener todo eso ya podemos meternos para comprobar que todo este bien:

<img width="1920" height="1080" alt="Captura de pantalla (865)" src="https://github.com/user-attachments/assets/ac72f6e8-db0d-4b9d-a0df-8563d621760f" />


<img width="1918" height="519" alt="Captura de pantalla 2025-09-15 233139" src="https://github.com/user-attachments/assets/358d5393-79cc-4bed-b7b2-18b15f1cc4e3" />


Podremos cobrar si estan de alta las paginas:

Wazuh Dashboard: https://<docker-host-ip>:8443

Login: admin | SecretPassword

MISP: https://<docker-host-ip>

Login: admin@admin.test | admin

The Hive: http://<docker-host-ip>:9000

Login: admin@thehive.local | secret

Cortex: http://<docker-host-ip>:9001

Login: admin | admin


<img width="1920" height="1080" alt="Captura de pantalla (867)" src="https://github.com/user-attachments/assets/7777da6d-732d-4f22-85f3-ce23b1df486d" />

<img width="1920" height="1080" alt="Captura de pantalla (871)" src="https://github.com/user-attachments/assets/31aeda06-8993-46af-a86b-d50520c6d6c7" />


<img width="1920" height="1080" alt="Captura de pantalla (868)" src="https://github.com/user-attachments/assets/26ead81e-2393-4c0d-95c3-7f1ce65634db" />


<img width="1920" height="1080" alt="Captura de pantalla (869)" src="https://github.com/user-attachments/assets/18ac0e53-c3b7-4f1e-837b-003f3146d017" />


<img width="1920" height="1080" alt="Captura de pantalla (870)" src="https://github.com/user-attachments/assets/984fdf9f-1803-4e23-bcc8-bb3639929774" />

<img width="1600" height="796" alt="image" src="https://github.com/user-attachments/assets/df87f4de-1f80-458b-b89f-7a6e956d1269" />

<img width="1600" height="721" alt="image" src="https://github.com/user-attachments/assets/37b0a18d-c9dc-436d-a8c2-0b86f81b405e" />




