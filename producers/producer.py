import requests
from typing import Dict, List, Tuple
from google.transit import gtfs_realtime_pb2
import time

from settings import (
    KAFKA_TOPIC,
)
from secrets import (
    API_KEY,
    AGENCY_KEY,
    SCHEMA_REGISTRY_URL,
    SCHEMA_REGISTRY_KEY,
    SCHEMA_REGISTRY_PASSWORD,
)

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext, MessageField


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


class VehicleLocationProducer:
    def __init__(self, props: Dict):
        self.key_serializer = StringSerializer()
        schema_registry_props = {
            "url": SCHEMA_REGISTRY_URL,
            "basic.auth.user.info": SCHEMA_REGISTRY_KEY
            + ":"
            + SCHEMA_REGISTRY_PASSWORD,
        }
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.value_serializer = ProtobufSerializer(
            gtfs_realtime_pb2.FeedEntity,
            schema_registry_client,
            conf={"use.deprecated.format": False},
        )

        # Producer Configuration
        self.producer = Producer(props)

    @staticmethod
    def read_records(api_key: str, agency_key: str):
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(
            f"http://api.511.org/Transit/VehiclePositions?api_key={api_key}&agency={agency_key}"
        )
        feed.ParseFromString(response.content)
        location_records, location_keys = [], []
        for entity in feed.entity:
            vehicle_id = entity.vehicle.vehicle.id

            location_records.append(entity)
            location_keys.append(vehicle_id)
        return zip(location_keys, location_records)

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            print("Delivery failed for record {}: {}".format(msg.key(), err))
            return
        print(
            "Record {} successfully produced to {} [{}] at offset {}".format(
                msg.key(), msg.topic(), msg.partition(), msg.offset()
            )
        )

    def publish(
        self, topic: str, records: List[Tuple[str, gtfs_realtime_pb2.FeedEntity]]
    ):
        for key_value in records:
            key, value = key_value
            try:
                self.producer.produce(
                    topic=topic,
                    key=self.key_serializer(
                        key, SerializationContext(topic=topic, field=MessageField.KEY)
                    ),
                    value=self.value_serializer(
                        value,
                        SerializationContext(topic=topic, field=MessageField.VALUE),
                    ),
                    on_delivery=self.delivery_report,
                )
            except Exception as e:
                print(f"Exception while producing record - {value}: {e}")
            finally:
                self.producer.flush()


if __name__ == "__main__":
    config = read_config()
    producer = VehicleLocationProducer(props=config)
    try:
        while True:
            vehicle_location_records = producer.read_records(API_KEY, AGENCY_KEY)
            producer.publish(topic=KAFKA_TOPIC, records=vehicle_location_records)
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nProducer stopping...")
    finally:
        producer.producer.flush()
