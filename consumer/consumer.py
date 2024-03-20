import os
from typing import Dict, List
from google.transit import gtfs_realtime_pb2

from confluent_kafka import Consumer
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from settings import (
    KAFKA_TOPIC,
)


def read_config():
    # reads the client configuration from client.properties
    # and returns it as a key-value map
    config = {}
    with open("./client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split("=", 1)
                config[parameter] = value.strip()
    return config


class VehicleLocationConsumer:
    def __init__(self, props: Dict):
        self.str_key_deserializer = StringDeserializer()
        self.protobuf_value_deserializer = ProtobufDeserializer(
            gtfs_realtime_pb2.FeedEntity,
            conf={"use.deprecated.format": False},
        )

        self.consumer = Consumer(props)

    def consume_from_kafka(self, topics: List[str]):
        self.consumer.subscribe(topics=topics)
        while True:
            try:
                # SIGINT can't be handled when polling, limit timeout to 1 second.
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                key = self.str_key_deserializer(
                    msg.key(), SerializationContext(msg.topic(), MessageField.KEY)
                )
                record = self.protobuf_value_deserializer(
                    msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
                )
                if record is not None:
                    print("{}, {}".format(key, record))
            except KeyboardInterrupt:
                break

        self.consumer.close()


if __name__ == "__main__":
    config = read_config()
    config["group.id"] = "vehicle.locations.consumer"
    config["auto.offset.reset"] = "earliest"
    avro_consumer = VehicleLocationConsumer(props=config)
    avro_consumer.consume_from_kafka(topics=[KAFKA_TOPIC])
