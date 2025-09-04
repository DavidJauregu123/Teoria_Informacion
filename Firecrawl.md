# 📘 Proyecto Firecrawl - Documentación

Este proyecto documenta el uso de **Firecrawl**, una herramienta para realizar scraping y extracción de datos de manera sencilla, ya sea a través de su plataforma web o mediante su **API**.

## 🚀 Introducción

**Firecrawl** es un servicio que permite explorar, rastrear y extraer información de sitios web de manera eficiente.  
Se puede usar de dos formas principales:
1. **Desde la plataforma web**: con herramientas interactivas y panel de control.
2. **Con la API**: para automatizar procesos desde tu propio código.

---

## 📝 Requisitos previos

- Conexión a Internet.
- Navegador web moderno (Chrome, Firefox, Edge).
- [Cuenta en Firecrawl](https://www.firecrawl.dev/app/logs).
- Para la API: tener **Python 3.8+** instalado.

---

## 🔑 Pasos para usar Firecrawl

### 1. Crear una cuenta
- Ve a [Firecrawl](https://www.firecrawl.dev/app/logs).
- Regístrate con tu correo electrónico o cuenta de GitHub/Google.
- Accede al **panel de control** donde podrás ver tus registros de uso.

### 2. Exploración de la plataforma
- Ingresa a tu **dashboard**.
- Explora las herramientas:
  - **Logs**: seguimiento de tus solicitudes.
  - **Scraping**: extracción de información de páginas.
  - **API Keys**: genera tus claves para usar la API.
- Haz una prueba ingresando una URL y observa cómo Firecrawl procesa los datos.

---

## 🛠️ Uso de la API

Si deseas automatizar el uso de Firecrawl en tu propio proyecto, puedes hacerlo con Python u otros lenguajes compatibles.

### 1. Instalación de dependencias
Ejecuta en tu terminal:

```bash
pip install firecrawl
````
### 2. En este caso utilizamos estos código de prueba utilizando la API, que creamos con anterioridad. 
- Código de Scrapeo: (https://github.com/DavidJauregu123/Teoria_Informacion/blob/04536ab51a5b73865cb1e659ff75f07a7ef5f7b5/scrapeo.py).
- Código de Mapeo: (https://github.com/DavidJauregu123/Teoria_Informacion/blob/04536ab51a5b73865cb1e659ff75f07a7ef5f7b5/mapeo.py).

### 3. Copia y pega estos codigos. (RECUERDA UTILIZAR TU PROPIO API KEY❗❗❗)
Corremos el código en cualquier ambiente de desarrollo que tu elijas, en este caso utilizaremos Visual Code: 


Te deberia quedar asi:
- ![Captura de pantalla del Scrapeo](https://github.com/DavidJauregu123/Teoria_Informacion/blob/c42845ad925ed2dec290453a62bbf087aeeded11/captura%20de%20mapeo.png) 
- ![Captura de pantalla del Mapeo](https://github.com/DavidJauregu123/Teoria_Informacion/blob/1ac0b29a335819eb69e57b8a61c7dafca0066b90/captura%20de%20mapeo.png)

### 4. Corremos los codigos en la terminal, y te deberia aparecer en la pagina de Firecrawl en la sección de Activity Logs.

Al realizar los llamados a la API, es importante que los resultados se muestren correctamente en tu sesión de Firecrawl iniciada, donde podrás visualizar los datos extraídos.

- ![Captura de pantalla](https://github.com/DavidJauregu123/Teoria_Informacion/blob/363134fe895140a7122b535e8e32ef47c0f3ea03/Activity%20Logs.png)

Descargas los archivos en formato MD o JSON. Y listo, ya hiciste tus primeros dos ejercicios utilizando la API de Firecrawl, una excelente herramienta para poder scrapear, y mapear de manera eficiente.


  






