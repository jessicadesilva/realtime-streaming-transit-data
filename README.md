# Real-time streaming pipeline from 511 API

![Architecture diagram](transit_data_streaming_diagram.drawio.png)

1. Clone this repository using
`https://github.com/jessicadesilva/realtime-streaming-transit-data.git`

1. Login to [Confluent Cloud](https://confluent.cloud/login)

1. Create a cluster in Google Cloud and make note of the region (e.g., `Los Angeles (us-west2)`). Once you have given the cluster a name (e.g., `dezoomcamp_cluster`), launch it.

1. We will now populate a `secrets.py` file with credentials from Confluent Cloud. First, create a `secrets.py` file in the `producers` folder of this project.

1. In Confluent Cloud, select `Environments` on the left navigation menu and the default environment. On the bottom right, copy the endpoint paste it into your `secrets.py` file in the following way:
`SCHEMA_REGISTRY_URL = "insert endpoint url here"`

1. In that same section of Confluence Cloud, create and download a (Schema Registry) API key. Copy and paste each of the key and password into the same `secrets.py` file in the following way:
```
SCHEMA_REGISTRY_KEY = "insert key here"
SCHEMA_REGISTRY_PASSWORD = "insert password here"
```

1. Create a topic called `vehicle_locations`, change the number of partitions to 2, and in `Advanced Settings` change the retention time to 1 day. Then select `Save and Create`.




https://github.com/jessicadesilva/realtime-streaming-transit-data/assets/74026509/3c7c0136-73dc-4d95-8311-f98bce824a77
 
