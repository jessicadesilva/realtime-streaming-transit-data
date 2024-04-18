# Real-time streaming pipeline from 511 API

![Architecture diagram](transit_data_streaming_diagram.drawio.png)

1. Clone this repository using
`https://github.com/jessicadesilva/realtime-streaming-transit-data.git`

1. Login to [Confluent Cloud](https://confluent.cloud/login)

1. Create a cluster in Google Cloud and make note of the region (e.g., `Los Angeles (us-west2)`). Once you have given the cluster a name (e.g., `dezoomcamp_cluster`), launch it.

1. We will now populate a `secrets.py` file with credentials from Confluent Cloud. First, create a `secrets.py` file in the `producers` folder of this project.

1. In Confluent Cloud, select `Environments` on the left navigation menu and the default environment. On the bottom right, copy the endpoint paste it into your `secrets.py` file in the following way:
`SCHEMA_REGISTRY_URL = "insert endpoint url here"`

1. In that same section of Confluent Cloud, create and download a (Schema Registry) API key. Copy and paste each of the key and password into the same `secrets.py` file in the following way:
```
SCHEMA_REGISTRY_KEY = "insert key here"
SCHEMA_REGISTRY_PASSWORD = "insert password here"
```
We have finalized the `secrets.py` file at this point.

1. In your default environment in Confluent Cloud, select the cluster we created. Create a topic called `vehicle_locations`, change the number of partitions to 2, and in `Advanced Settings` change the retention time to 1 day. Then select `Save and Create`.

1. We will now need to create a service account in the Google Cloud Platform (GCP) that will allow us to sink the streaming data to BigQuery. Login to the [Google Cloud Platform](https://https://console.cloud.google.com/) and create a project if you don't want to use an existing one. In IAM & Admin, create a BigQuery Admin service account and add a key (which downloads a json file). In BigQuery, create a dataset called `511_transit_data` and ensure that the region matches the cluster region from Confluent Cloud. Within the dataset, create a table called `vehicle_locations` and ensure it is partitioned by ingestion time with a per-hour partitioning time.

1. Back in our cluster in Confluent Cloud, select Connectors in the left navigation menu and select the `Google BigQuery Sink V2` connector. Select the topics we created and download the API Key with Global Access (we won't use this API key). Upload the service account key file downloaded from GCP. Input your project id from GCP and dataset name (`511_transit_data`). Keep the option set to `STREAMING` and select `PROTOBUF` for the Input Kafka record value format. Under Advanced Configurations, set Auto Create Tables to `Partition by Ingestion Time` and set the partitioning type to `HOUR`. Keep the default settings for the rest of the creation of the connector.






https://github.com/jessicadesilva/realtime-streaming-transit-data/assets/74026509/3c7c0136-73dc-4d95-8311-f98bce824a77
 
