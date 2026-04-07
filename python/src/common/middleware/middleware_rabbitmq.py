import pika
import random
import string
from .middleware import MessageMiddlewareCloseError, MessageMiddlewareQueue, MessageMiddlewareExchange

class MessageMiddlewareQueueRabbitMQ(MessageMiddlewareQueue):

    def __init__(self, host, queue_name):
        self.queue_name = queue_name
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host)
            )
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=self.queue_name)

        except pika.exceptions.AMQPConnectionError:
            print(f"Error conectando a RabbitMQ en {host}")
            raise

    def close(self):
        try:
            if self._connection.is_open:
                self._connection.close()
        except Exception:
            raise MessageMiddlewareCloseError()

    def send(self, message):
        pass

    def start_consuming(self, on_message_callback):
        pass

    def stop_consuming(self):
        pass

class MessageMiddlewareExchangeRabbitMQ(MessageMiddlewareExchange):
    
    def __init__(self, host, exchange_name, routing_keys):
        pass
