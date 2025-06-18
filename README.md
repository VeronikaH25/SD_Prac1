# Análisis de Escalabilidad en Sistemas Distribuidos Usando Middleware de Comunicación Directa e Indirecta

Este proyecto tiene como objetivo analizar el comportamiento y la escalabilidad de sistemas distribuidos utilizando diferentes tecnologías de middleware de comunicación. Se implementan dos aplicaciones escalables: el **InsultService** y el **InsultFilter**. Estos servicios se desarrollan y prueban utilizando las tecnologías de **XMLRPC**, **PyRO**, **Redis** y **RabbitMQ**.

### Descripción de los Servicios:

## Instalación

Para utilizar este proyecto, clona o descarga todo el repositorio en tu máquina local. Asegúrate de tener instalado **Python 3.8 o superior** y **pip**.

###  Instalación de Visual Studio 
Para la realización tanto de la practica como de las pruebas hemos utilizado VisualStudio por tanto recomendamos instalar este.

Dependiendo de tu sistema operativo y necesidades:

Descarga oficial: https://visualstudio.microsoft.com/es/downloads/

## Instalación de los Middleware

### 1. XML-RPC (Integrado en Python)
No requiere instalación adicional en Python 3.x (viene en la librería estándar).  
Puedes verificar su disponibilidad con:
```bash
python -c "import xmlrpc"
````

### 2. PyRO (Python Remote Objects)
```bash
pip install Pyro5
````

### 3. Redis 
Descarga e instala Docker Desktop según tu sistema operativo:
-Windows/macOS: Descargar Docker Desktop
-Linux (Ubuntu/Debian):
````bash
sudo apt update
sudo apt install docker.io
sudo systemctl enable --now docker
````
Una vez instalado abrimos una terminal(CMD):
````bash
docker run --name my-redis -p 6379:6379 -d redis
````

### 4. RabbitMQ 
Descarga e instala Erlang según tu sistema operativo:

-Instalación en Windows:

Descargar instalador desde https://www.rabbitmq.com/install-windows.html.

También hay que instalar Erlang.

IMPORTANTE usar siempre la versión compatible con tu versión de RabbitMQ:
https://www.erlang.org/downloads

-Instalación en Linux:
```bash
sudo apt update
sudo apt install -y erlang rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```


### Una vez todo instalado procedemos a hacer pruebas:

Las pruebas de XML-RPC,PyRO,REDIS,RabbitMQ se pueden realizar de las siguientes formas una vez abierto el proyecto:

FORMA 1)

Individualmente abres el PATH hasta llegar a la carpeta corresponiente al middleware de donde estan los codigos que quieres ejecutar.

Por ejemplo:
```bash
cd .\redis_version\
````
Y allí ejecutas alguno por inidvidual que quieras hacer por ejemplo:
```bash
python insult_filter.py
```
Y asi lo puedes probar con cualquiera de los codigos que quieras ejecutar.

FORMA 2) 

Al igual has de abrir el path hasta llegar a la carpeta corresponiente al middleware para ejecutar los tests.
Eliges cual de los tests quieres ejecutar.

Para modificar tanto el numero de nodos como las requests en la parte del main hay dos variables que puedes modificar.
```bash
python redis_filter_test.py
```
Alli en el terminal se pueden ver los resultados de lo que han dado los test.

### MULTIPLE-NODE DYNAMIC TEST
Estas son las instrucciones para ejecutar el dynamic en nuestra practica. 
```bash
pyro4-ns
```
Si ya habias ejecutado anteriormente tendras que hacer FLUSHDB en el Docker
```bash
docker exec ny-redis redis-cli FLUSHDB
```
Seguidament abre una nueva terminal y ejecuta el insult_filter_pyro.py
```bash
python insult_flter_pyro.py --port 9091 --name insult_filter
```
En otra termial ejecuta el autoscaler
```bash
python autoscaler.py
```
Finamente en una tercera ejeuta el broadcaster 
```bash
python insult_broadcaster.py
```
La terminal de autoscalar.py mostrará los mensajes que hay en la cola y los workers que tiene activos, así como un mensaje cada vez que incrementa o decrementa los workers.