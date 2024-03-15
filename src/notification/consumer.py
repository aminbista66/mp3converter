from confluent_kafka import Consumer, Message
import os
from confluent_kafka.error import KafkaError, KafkaException
import sys
import send

class MP3Consumer:
    consumer: Consumer
    topics: list[str]

    def __init__(self) -> None:
        self.topics = ["mp3_topic"]

        self.consumer = Consumer(
            {
                "bootstrap.servers": os.environ.get("KAFKA_CLUSTER_SERVER"),
                "bootstrap.servers": os.environ.get("KAFKA_CLUSTER_SERVER"),
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": "PLAIN",
                "sasl.username": os.environ.get("KAFKA_CLUSTER_USERNAME"),
                "sasl.password": os.environ.get("KAFKA_CLUSTER_SECRET"),
                "group.id": os.environ.get("KAFKA_CONSUMER_GUID"),
                "auto.offset.reset": "earliest",
            }
        )

    def run(self):
        try:
            print(self.topics)
            self.consumer.subscribe(topics=self.topics)
            print("Subcribed to topic: {} listening....".format(self.topics))

            while True:
                msg: Message | None = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:  # type:ignore
                        # End of partition event
                        sys.stderr.write(
                            "%% %s [%d] reached end at offset %d\n"
                            % (msg.topic(), msg.partition(), msg.offset())
                        )
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    self.consumer.commit(asynchronous=False)
                    print(
                        "Consumed message: value={value}, key={key}".format(
                            value=msg.value().decode("utf-8"),  # type:ignore
                            key=msg.key().decode("utf-8"),  # type:ignore
                        )
                    )
                    send.notification(msg.value())

        except KeyboardInterrupt:
            print("exitting...")
        finally:
            # Close down consumer to commit final offsets.
            print("closing consumer...")
            self.consumer.close()
