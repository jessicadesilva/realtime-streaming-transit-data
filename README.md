# Real-time streaming pipeline from 511 API

The goal of this project is to visualize the real-time locations of public buses in the San Francisco Bay Area. In particular, we will use data provided by the 511 Transit API to create a dashboard visualizing the locations of AC Transit buses with a refresh rate of 10 seconds. We will also create a pie chart which visualizes the proportion of buses which have a vehicle status in any one of these categories: stopped, arriving at a stop, heading towards a stop, and unknown. The architecture diagram can be found below.

![Architecture diagram](transit_data_streaming_diagram.drawio.png)

1. Clone this repository using
`https://github.com/jessicadesilva/realtime-streaming-transit-data.git`

1. Login to [Confluent Cloud](https://confluent.cloud/login)

1. Create a cluster in Google Cloud and make note of the region (e.g., `Los Angeles (us-west2)`). Once you have given the cluster a name (e.g., `dezoomcamp_cluster`), launch it.

1. We will now create a `client.properties` file which will allow us to connect to the Kafka cluster. In Confluent Cloud, select `Clients` on the left navigation menu and select Python. Skip step 2 and go to step 3, copy the code snippet and it will ask if you want to create a new Kafka cluster API Key so select Yes. The API key and password will now appear where necessary. In the main folder of your project, create a `client.properties` file and paste the code you copied. It should look something like this:
```
# Required connection configs for Kafka producer, consumer, and admin
bootstrap.servers=pkc-12576z.us-west2.gcp.confluent.cloud:9092
security.protocol=SASL_SSL
sasl.mechanisms=PLAIN
sasl.username=USERNAMEHERE
sasl.password=PASSWORDHERE

# Best practice for higher availability in librdkafka clients prior to 1.7
session.timeout.ms=45000
```

1. We will now populate a `secrets.py` file with credentials from Confluent Cloud. First, create a `secrets.py` file in the `producers` folder of this project.

1. Request a free token from the [511 Transit Data](https://511.org/open-data/token) website. You will receive an email asking you to fill out a form, in the form request a token for transit data. You will then receive an email with the token and you should include the following two lines in your `secrets.py` file with the token filled in:
```
API_KEY = "INSERT KEY HERE"
AGENCY_KEY = "AC" # leave as is
``` 

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

1. Now that we have everything setup in Confluent Cloud, we will start creating connections to our Dashboard. For realtime visualization, we will be using [Grafana](https://grafana.com). Create a (free) account and launch their Grafana product.

1. Navigate to Connections on the left menu panel and install the Google BigQuery connector. Create a new data source and upload the credentials file for the GCP service account with BigQuery Admin access we created. In additional settings, ensure that the processing location matches the location where the table is hosted in BigQuery (e.g., `Los Angeles (uswest-2)`). Click Save & Test.

1. Still in Grafana, navigate to Dashboards on the left and create a new dashboard. Add a visualization using the data source we just created. Change the visualization type to GeoMap. Title it `Realtime 511 transit map`, change the `View` option in Map View to `Fit to Data`, set `Padding` to `1`, in the Markers section change `Value` to `2`, and `Opacity` to `0.4`. On the bottom panel select `Code` and use the following SQL query where PROJECT_ID is replaced with your GCP project ID:

```
WITH time_table AS (
  SELECT vehicle.vehicle.id AS vehicle_id, MAX(vehicle.timestamp) AS recent_time
  FROM `PROJECT_ID.511_transit_data.vehicle_locations`
  GROUP BY 1
)
SELECT
geo.vehicle.position.latitude AS latitude,
geo.vehicle.position.longitude AS longitude,
geo.vehicle.vehicle.id AS vehicle_id
FROM `PROJECT_ID.511_transit_data.vehicle_locations` AS geo
INNER JOIN time_table ON (time_table.vehicle_id = geo.vehicle.vehicle.id AND time_table.recent_time = geo.vehicle.timestamp)
```

1. Apply the changes to the visualization.

1. Create a new visualization and change the type to Pie Chart. Title it `Vehicle Status`, under Value Options toggle from Calculate to `All Values`. On the bottom panel, select Code and use the following SQL query where PROJECT_ID is replaced with your GCP project ID:

```
WITH time_table AS (
  SELECT vehicle.vehicle.id AS vehicle_id, MAX(vehicle.timestamp) AS recent_time
  FROM `PROJECT_ID.511_transit_data.vehicle_locations`
  GROUP BY 1
)
SELECT
CASE 
  WHEN geo.vehicle.current_status IS NULL THEN 'UNKNOWN'
  ELSE geo.vehicle.current_status
END AS current_status,
COUNT(*) AS number_of_vehicles
FROM `PROJECT_ID.511_transit_data.vehicle_locations` AS geo
INNER JOIN time_table ON (time_table.vehicle_id = geo.vehicle.vehicle.id AND time_table.recent_time = geo.vehicle.timestamp)
GROUP BY geo.vehicle.current_status
```

1. Apply the changes to the visualization.

1. In the upper right corner of the dashboard, set the Auto Refresh rate to 10 seconds. No data will be showing yet since we don't have our producers running, but we will come back to this once they are.

1. Start up Docker and, in the terminal, navigate to the project directory and run the command `docker-compose up -d`.

1. Once all the services are up and running, run `python ./consumer/consumer.py` in your terminal.

1. In another terminal still navigated to the main project directory, run `python ./producers/producer.py`. You should see the messages being sent and received immediately. In Grafana, you should also now see your map populated with the locations of the vehicles with a refresh rate of 10 seconds, and the pie chart refreshing at the same rate. The map should look something like this:

https://github.com/jessicadesilva/realtime-streaming-transit-data/assets/74026509/3c7c0136-73dc-4d95-8311-f98bce824a77
 
1. Once you are done with the project, don't forget to delete all of the resources in Confluence Cloud and the dataset in BigQuery to avoid being billed.