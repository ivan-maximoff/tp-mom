import pika
import random
import string
from .middleware import MessageMiddlewareCloseError, MessageMiddlewareDisconnectedError, MessageMiddlewareMessageError, MessageMiddlewareQueue, MessageMiddlewareExchange

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
        try:
            self._channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message
            )
        except pika.exceptions.AMQPConnectionError:
            raise MessageMiddlewareDisconnectedError()
        except Exception:
            raise MessageMiddlewareMessageError()

    def start_consuming(self, on_message_callback):
        def internal_callback(ch, method, _, body):
            def ack():
                ch.basic_ack(delivery_tag=method.delivery_tag)
            def nack():
                ch.basic_nack(delivery_tag=method.delivery_tag)
            on_message_callback(body, ack, nack)

        try:
            self._channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=internal_callback
            )
            self._channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            raise MessageMiddlewareDisconnectedError()
        except pika.exceptions.ConnectionClosedByBroker:
            pass

    def stop_consuming(self):
        try:
            if self._channel and self._channel.is_open:
                self._channel.stop_consuming()
        except Exception:
            pass

class MessageMiddlewareExchangeRabbitMQ(MessageMiddlewareExchange):
    
    def __init__(self, host, exchange_name, routing_keys):
        pass
