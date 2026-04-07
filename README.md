# Trabajo Práctico - Middlewares Orientados a Mensajes

Los middlewares orientados a mensajes (MOMs) son un recurso importante para el control de la complejidad en los sistemas distribuídos, puesto que permiten a las distintas partes del sistema comunicarse abstrayéndose de problemas como los cambios de ubicación, fallos, performance y escalabilidad.

En este repositorio se proveen conjuntos de pruebas para los dos formas más comunes de organización de la comunicación sobre colas, que en RabbitMQ se denominan Work Queues y Exchanges.

Se recomienda familiarizarse con estos conceptos leyendo la documentación de RabbitMQ y siguiendo los [tutoriales introductorios](https://www.rabbitmq.com/tutorials).

## Condiciones de Entrega

El código de este repositorio se agrupa en dos carpetas, una para Python y otra para Golang. Los estudiantes deberán elegir **sólo uno** de estos lenguajes y completar la implementación de las interfaces de middleware provistas con el objetivo de pasar las pruebas asociadas.

Al momento de la evaluación y ejecución de las pruebas se **descartarán** los cambios realizados a todos los archivos, a excepción de:

**Python:** `/python/src/common/middleware/middleware_rabbitmq.py`

**Golang:** `/golang/internal/factory/*/*.go`

## Ejecución

`make up` : Inicia contenedores de RabbitMQ y de pruebas de integración. Comienza a seguir los logs de las pruebas.

`make down`: Detiene los contenedores de pruebas y destruye los recursos asociados.

`make logs`: Sigue los logs de todos los contenedores en un solo flujo de salida.

`make local`: Ejecuta las pruebas de integración desde el Host, facilitando el desarrollo. Se explica con mayor detalle dentro de su sección.

## Pruebas locales desde el Host

Habiendo iniciado el contenedor de RabbitMQ o configurado una instancia local del mismo pueden ejecutarse las pruebas sin necesidad de detener y reiniciar los contenedores ejecutando `make local`, siempre que se cumplan los siguientes requisitos.

### Python

Instalar una versión de Python superior a `3.14`. Se recomienda emplear un gestor de versiones, como ser `pyenv`.
Instalar los dependencias de la suite de pruebas:
`pip install -r python/src/tests/requirements.txt`

### Golang

Instalar una versión de Golang superior a `1.24`.
Instalar los dependencias de la suite de pruebas:
`go mod download`

## Mi solución en Python

Para reducir la duplicación, incorporé un comportamiento base compartido para las partes que eran prácticamente iguales entre ambas variantes del middleware.

### Resumen del diseño

- Clase base común (`_RabbitMQMiddleware`): Centraliza la configuración de la conexión y las operaciones compartidas.
  - Manejo del ciclo de vida de conexión/canal (`__init__`, `close`).
  - Abstracción de errores: Traducción de excepciones nativas de Pika (AMQPConnectionError) a las excepciones de dominio del TP.
  - Método auxiliar para publicar mensajes (`_publish`).
  - Flujo común de consumo (`start_consuming`, `stop_consuming`) con métodos de callback para `ack`/`nack`.
- Las clases concretas conservan únicamente el comportamiento específico:
  - `MessageMiddlewareQueueRabbitMQ`: Implementa Work Queues.
  - `MessageMiddlewareExchangeRabbitMQ`: Implementa el patrón Pub/Sub (Exchanges).

### Decisiones de Implementación

- **Tipo de exchange:** Se utilizó un exchange de tipo `direct`.
- **Envío (`send`):** El método `send` realiza un "broadcast manual", iterando sobre todas las routing keys configuradas para asegurar que el mensaje llegue a todos los destinos.
- **Colas temporales:** En el patrón de Exchange, cada consumidor genera una cola exclusiva (`exclusive=True`) para garantizar que reciba su propia copia de los mensajes.
