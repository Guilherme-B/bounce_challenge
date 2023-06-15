# Bounce Challenge


1. [Exercise 1 - Python Script for Data Extraction from REST API](#exercise-1)
2. [Exercise 2 - Advanced SQL Query for Time-based Events Analysis](#exercise-2)
3. [Exercise 3 - Geospatial Modeling Challenge](#exercise-3)
4. [Exercise 4 - Cloud-based Data Stack Architecture Documen](#exercise-4)

## [Exercise 1 - Python Script for Data Extraction from REST API](#exercise-1)

Your first task is to write a Python script to extract data from the GitHub API. The API returns paginated responses for repository data. Your script should be able to handle paging, cursors, and authentication and should store the extracted data in a suitable format for further analysis.

Here's the API endpoint you need to extract data from: `https://api.github.com/users/bounceapp/repos`

### Requirements:

1. Implement paging logic to retrieve all repositories of the user.
2. Handle cursor-based pagination if applicable.
3. Handle API authentication.
4. Save the data in a CSV format for further analysis.

### Assumptions

- The implementation must be manual and not use any existing library such as PyGithub (https://github.com/PyGithub/PyGithub) or Scrapy
- The implementation must be sequential due to the linear dependency of the cursor pagination meaning, no multi-threading nor Asyncio implementations are valid

#### Future Work
- Replace the custom library with a set of existing, heavily tested implementations such as Scrapy and PyGithub
- Add unit and integration tests
- Add a CI/CD for the target deployment platform

### Solution

Notes: The challenge requires saving the data in CSV. Given it is unstructured data, I would opt instead to store it in an optimized format (Parquet, Delta) or as an alternative, JSON.

> The implementation can be found in the `bounce_challenge/*`, `main.py`, `setup.py` directories

Note: In order to use the authentication via Token, make sure the `AUTH_TOKEN` environment variable is set

To start the process execute the following command:
> `bounce_challenge --s github_repositories --u bounceapp --o data.csv --use_token`

| Argument Name | Short Option | Long Option | Type | Is Optional | Example |  Description | Default Value |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |------------- |------------- |
| Scraper  | `--s`  | `--scraper_name`  | String  | False | `--scraper_name github_repositories` | The name of the scraper instance to be initialized |  |
| Scraper  | `--u`  | `--user_name`  | String  | False | `--user_name bounce-app` | The user name to be scraped | |
| Scraper  | `--o`  | `--output_path`  | String  | False | `--output_path data.csv` | The output path where to store the extracted data |  |
| Scraper  | `--t`  | `--use_token`  | Flag  | True | `--use_token` | Should a token be used for authentication (stored in Env variable `AUTH_TOKEN`) | |
| Scraper  | `--f`  | `--filters_list`  | String List  | False | `--filters_list user_id, repo_id` | A list of extracted data attributes to be selected | `id, node_id, name, full_name, private,html_url, description ,fork,url, created_at, updated_at, pushed_at, git_url, ssh_url, clone_url, homepage, size, has_issues, has_projects, has_downloads, archived, disabled, license, visibility, watchers` |

## [Exercise 2 - Advanced SQL Query for Time-based Events Analysis](#exercise-2)

Imagine you have an e-commerce dataset with the following three tables:

1. `orders` (columns: `order_id`, `customer_id`, `product_id`, `order_time`, `quantity`)
2. `products` (columns: `product_id`, `product_name`, `category`, `price`)
3. `customers` (columns: `customer_id`, `registration_date`, `country`)

Write a SQL query that returns the top 3 products in each category with the highest total sales in the past week, but only for the customers that registered in the past year. Also, filter out the results for the categories that have total sales of less than 100 units in the past week. Please use window functions to accomplish this.

### Solution


> The implementation can be found in the `resources/exercise_2.sql` file or below.

```sql
WITH category_prev_week_ AS (
  /*
    select the categories whose previous week's performance was below 100 sold units

    note that the outer query below cannot be leveraged to perform this computation directly,
    as that would mean filtering the categories at the Product level, whereas the goal
    is to filter based on the category's own behavior. 
      in practice this could be achieved by filtering on the JOIN predicate, see notes
      in the assumptions section.
  */
  SELECT
    products.category
  FROM
    orders
  INNER JOIN
    products
  ON
    orders.product_id = products.product_id
  WHERE
    -- filter dates whose order time is in the past week (between the previous week's Monday and Sunday)
    orders.order_time BETWEEN DATE_TRUNC('week', current_date - interval '1 week')::DATE AND (DATE_TRUNC('week', current_date - interval '1 week') + interval '6 days')::DATE
  GROUP BY
    products.category
  HAVING
    -- filter out the results for categories that have total sales less than 100 units in the past week
    SUM(orders.quantity) < 100
)

SELECT
  -- top 3 products in each category with the highest total sales in the past week
  ROW_NUMBER() OVER (PARTITION BY products.category ORDER BY SUM(orders.quantity) DESC) AS category_rank,
  products.category,
  products.product_name,
  COUNT(DISTINCT orders.order_id) orders_qty,
  SUM(orders.quantity) orders_amt
FROM
  orders
INNER JOIN
  products
ON
  orders.product_id = products.product_id
INNER JOIN
  customers
ON
  orders.customer_id = customers.customer_id
WHERE
  -- filter orders from Customers whose registration year is in the past year
  YEAR(customers.registration_date) = YEAR(GETDATE()) -1
  AND
  -- filter dates whose order time is in the past week (between the previous week's Monday and Sunday)
  orders.order_time BETWEEN DATE_TRUNC('week', current_date - interval '1 week')::DATE AND (DATE_TRUNC('week', current_date - interval '1 week') + interval '6 days')::DATE
  AND
  -- filter out the results for categories that have total sales less than 100 units in the past week
  products.category IN (SELECT category FROM category_prev_week_)
GROUP BY
  products.category,
  products.product_name
QUALIFY
  category_rank < 4
```

### Assumptions

Configuration assumptions:
- The underlying database is a Postgres instance
- The underlying database's local timezone is in the same timezone as the intended analysis
- Weeks start on Monday and end on Sundays
- Note: Whilst filtering the categories directly in the JOIN clause would be clearer, it can cause significant performance issues contingent on the query optimizer, for this reason, a CTE was used instead to allow for easier intermmediate materialization

Data assumptions:
- The underlying orders table corresponds to a header-item level table meaning, the table will contain the same `order_id` for each line-item

Note: All operations use ANSI SQL only to ensure cross-platofrm compatibility

## Exercise 3 - Geospatial Modeling Challenge](#exercise-3)

For this task, imagine we have an application where users check into various locations and these check-ins are recorded with geospatial data. We want to create a heatmap of these check-ins.

Design a data model (schema) that would support this use-case. This should include the data types and the relationships between tables if multiple tables are required.

Provide the SQL commands necessary to create this schema.


### Solution


> The implementation can be found in the `resources/exercise_3.sql` file.

- The methodology employs a Kimball (Star schema) design, directed towards the ability of creating heatmaps per user check-in under a time-aware situation with a high emphasis on local geographical markets.
  The reasoning behind using Kimball is due to its simplicity in implementation and maintanability, as well as direct compatibility with most BI tools, avoiding expensive JOINs where possible, ideal for a small company with a small data team.
- In practice, given that for Bounce's case over 10.000 locations are supported, these tables are very likely to grow exponentially. With this in mind, three optimizations take place:
  - The H3 indexes (Uber's H3, https://h3geo.org/) are included, in addition to WOF (Whosonfirst https://whosonfirst.org/) polygons for administrative levels 0, 1 and 2
  - Aggregate tables created for H3 indexes at resolution 9
  - Indexes on the main lookups (polygons and time) are introduced
- For the sake of simplicity, a Postgres framework has been used note however, that for analytical solutions at scale, Postgres should be disregarded over big data solutions explored in Exercise 4.

Note: The solution is highly contingent on the queries defined above else, the coordinates, WOF polygons and H3 hexes could all be combined into a single Junk dimension. 
      However, that due to the high cardinality and low-reuseability of GPS coordinates there is a risk of having the Dimensions grow on a near-linear fashion with the Facts, a clear indicator of a poorly designed schema.
      For this reason, the Polygons and H3 indexes have been split into separate dimensions, adding flexibility at the cost of additional maintenance complexity and extra joins.


| Table Name  | Table Type | SCD Type | Entity | Descripton |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| dim_user  | Conformed Dimension  | Type 1  | `(email_address, is_guest_customer)` | Dimension representing a User/Customer instance |
| dim_location  | Conformed Dimension  | Type 1  | `coordinates`  | Dimension representing a Coordinate and its characteristics |
| dim_spatial_index  | Conformed Dimension  | Type 1  | `h3_hex`  | Dimension representing a H3 spatial Hex used to aggregate information efficiently |
| dim_date  | Conformed Role-Playing Dimension  | Type 0  | `date_actual`  | Dimension representing a date |
| dim_time  | Conformed Role-Playing Dimension  | Type 0  | `time_id`  | Dimension representing time considering hour, minute and second units |
| fact_checkin  | Fact Transaction  | Type 1  | `(user_id, checkin_location_id, checkin_standard_date_id, checkin_standard_time_id)`  | Fact table representing the transactional check in events per user |
| fact_checkin_h3_res9_agg  | Fact Periodic Snapshot  | Type 1  | `(checkin_location_id, checkin_standard_date_id)`  | Aggregate fact table representing a summary of checkings per H3 spatial index per day |

Note: All column descriptions and types have been moved onto the corresponding `.sql` to make the current document readable.


![Data Model](resources/data_model_diagram.PNG?raw=true "Data Model")

### Assumptions

- The main assumption is related with how the data will be queried. In this specific case, it is assumed that users will most likely query via H3 indexes under a level 9 resolution for a given time period.
- In addition, PostgresSQL with Postgis extension enabled has been assumed as it introduces several geometric capabilities including but not limited to, spatial indexing
- Regarding the heavy usage of indexes, the assumption is that the cost of maintaining and adding new indexes is low compared with the compute and availability costs


## [Exercise 4: Cloud-based Data Stack Architecture Document](#exercise-4)

Lastly, create a document that describes an architecture for a modern cloud-based data stack. Your architecture should include tools for extraction (ETL), transformation, and analytics.

The document should:

1. Specify the tools/services you recommend for each layer in the stack and provide a brief rationale for each choice.
2. Provide a diagram showing the flow of data through this architecture.
3. Explain any important considerations or trade-offs involved in designing this architecture.

You're free to assume any reasonable constraints or requirements not explicitly stated in the prompt. However, please do note your assumptions clearly in your document.

---

Feel free to improve or remove as your solution evolves. Ideally, you would take advantage of git in order to do so, by doing some commits in the repository you will share with us. However, if you feel like there are improvements that you can do but have no time, just create some TODO comments that we will use to discuss with you later.

Your solution should include:

- Your Python scripts.
- A `.sql` file containing your SQL query and data model.
- Your architecture document, any format.
- A `README` file that includes any necessary instructions for running your scripts and an explanation of your work.


### Solution

The tools in each scenario have been selected by balancing the following main topics:
- Scalability: how well does each tool scale according to the 4 V's of Data
- Cost: how does the cost evolve as scale increases
- Integration: how well does the tool integrate with the remainder of the stack to streamline data flow and avoid complex integrations
- Latency: tools must be selected according to the latency needs, in other words, how often does data need to be updated?
- Complexity: what is the effort to create new pipelines or evolve the existing ones in the tool?
- Skill Set: are the skills and expertise required for the stack readibly available on the market at a price range which fits the budget?



Note: In practice DbT can be set to leverage Spark as well, creating a common ground and middle-term between the first and second scenarios, combining DbT's simplicity with Spark's flexibility.

#### Scenario 1

The first scenario corresponds to that of a startup environment, where a small team is focusing in finding answers fast and fast iterations, where development speed is valued over costs and scalability with a focus in self-serve analytics. Lastly, the focus is mainly in batch operations. The architecture corresponds to a traditional Data Warehousing platform, solely capable of batch processing pipelines.

Typical roles and responsibilities:
- Ingestion / Transformation: Analytics Engineer
- Analysis / Science / Visualization: Data Analyst


#####  Architecture walkthrough

1. Data is ingested from various operational sources via Fivetran into a Database (AWS Redshift, GCP BigQuery, Azure Synapse Analytics)
2. Fivetran performs a pre-transformation of data and stores it into a Database (Landing layer)
3. DbT is then used to perform the required transformations to model the data into the appropriate format, in a batch pipeline (Staging layer)
4. The Data is transformed within the same Database (OLAP) and stored as a Presentation layer (Presentation layer)
5. A Semantic layer is used to abstract access to the underlying tables and manage governance (AWS Redshift, GCP BigQuery, Azure Synapse Analytics)

Data Quality and Data Catalog are both ensured by DbT.

#####  Architecture diagram


![Data Platform - Scenario 1](resources/data_platform_scenario_1.png?raw=true "Data Platform - Scenario 1")


#####  Architecture layer breakdown


| Layer          | Solution      | Rationale (Pros) | Trade-off (Cons) | Stakeholder |
| -------------  | ------------- | ------------- | ------------- | ------------- |
| Ingestion      | Fivetran      | Fivetran automates the process of extracting data from the most common platforms. It is a battle tested platform with dedicated support and low maintenance, all three are critical aspects to drive fast results with low maintenance. | Fivetran provides little customization and its closed-source nature implies that any downtime directly affects the Platform without a reliable alternative. |Data/Analytics Engineer |
| Transformation      | DbT      | DbT provides a simple user-friendly interface and SQL-based syntax, making it easier for users without expert knowledge in programming and data pipelines, to contribute thus not requiring expensive and scarce human resources. In addition, SQL-based transformations facilitate rapid iterations and deployment. |  DbT scales rather poorly, depending on an underlying database for execution which introduces additional cost and performance considerations. In addition, maintaining large SQL repositories is a rather complex task, relying on the goodwill of users to properly document the code. SQL is rather limited in terms of its processing and transformation capabilities, it is designed for querying, not for transformations. Lastly, DbT lacks real-time integration. |Data/Analytics Engineer |
| Storage / Compute      | AWS Redshift, GCP BigQuery, Azure Synapse Analytics, Snowflake      | DbT requires an underlying database to run its transformation. Most cloud vendors provide scalable Data Warehousing solutions which DbT is prepared to leverage | Closed-source solutions imply vendor lock-in with all that it encompasses. In addition, alongside with the usage of DbT, the capabilities are dictated solely by the vendor's SQL implementations |Data/Analytics Engineer |
| Orchestration      | Apache Airflow, Dagster      |  |  |Data/Analytics Engineer |
| Visualization      | Excel, Looker & SQL      | Simple tools which allow for most users to create their own analysis and reports without relying on the time of Data Analysts | Looker has low modularity meaning, the reuseability of data models and the associated metrics layer, is low, forcing users to constantly redefine or refine the existing metrics. At the same time, the visualization capabilities offered by Looker are exceedingly simple. With this in mind, users often find themselves having to create their own analysis and data extraction via SQL, a fairly uncommon skillset for non-IT stakeholders |Data/Analytics Engineer |
| Data Quality      | DbT      | Simple data quality layer which is easy to implement | Relies on SQL code not allowing for a properly distributed DQ layer with complex rules |Data/Analytics Engineer |
| Data Catalog      | DbT      | Automatic Data Lineage | Simple lineage, not available for external Stakeholders |Data/Analytics Engineer |

#### Scenario 2

The second scenario corresponds to that of a scaleup environment, where the Data teams are starting to enlarge and focus in developing complex, maintaneable and scalable infrastructures with an increasing focus in diverse teams (self-serve Stakeholders, Data Scientists, ML Engineers, Data Eneigners, Analytics Engineers), cost and scalability are increasingly important. Lastly, a more diverse type of workload is required, including batch, microbatch and streaming pipelines. In a nutshell, the architecture is based on a Lakehouse architecture, adaptable to both Lambda and Kappa achitectures.

Typical roles and responsibilities:
- Ingestion: Data Engineer
- Transformation: Data Engineer / Analytics Engineer
- Analysis / Visualization: Data Analyst
- Data Science: Data Scientist
- ML Deployment: Machine Learning Engineer

#####  Architecture walkthrough

1. Data Ingestion
1.1 Data is ingested from various operational sources via Fivetran or Airbyte into a Data Lake in an unstructured format (1)
1.2 Data can also be injected directly from third parties into the Data Lake or Spark allowing for mini-batch or real-time workloads (2)
2. Spark retrieves the newly arrived data and pre-processes it, cleans it and reshapes it into an intermmediate historical-accurate layer named, Silver layer (3, 4) and generates the corresponding CDC
3. Spark ingests the CDC from the Silver layer and transforms it into the Gold layer into two separate levels (5):
3.1 Aggregates layer (6) - An intermmediate resource to be used by Data Analysts and Scientists with the full-spectrum Data
  Note: Data Warehouses typically do not include all information, only that which is of Analytical value and structured hence, this layer allows for unbiased access
3.2 Data Warehouse layer (7) - The final presentation layer made available to stakeholders and analytics resources
4. A Semantic layer is used to abstract access to the underlying tables and manage governance (AWS Redshift, GCP BigQuery, Azure Synapse Analytics) (8)

Data Quality is insured by Spark libraries such as Great Expectations and Data Catalog by the native platform, for instance, Databricks Unity catalog.

Note: Under a lakehouse architecture, no historical changes are ever lost. From the raw to presentation data, everything can be tracked, autited and reprocessed.

#####  Architecture diagram


![Data Platform - Scenario 2](resources/data_platform_scenario_2.png?raw=true "Data Platform - Scenario 2")


#####  Architecture layer breakdown

| Layer          | Solution      | Rationale (Pros) | Trade-off (Cons) | Stakeholder |
| -------------  | ------------- | ------------- | ------------- | ------------- |
| Ingestion      | Airbyte/Fivetran, Kafka (alongside Airbyte/Fivetran, AWS Kinesis, GCP Pub/Sub or Azure Event Hubs)  | |  |Data/Analytics Engineer |
| Transformation      | Apache Spark  (Databricks, AWS EMR/Glub, GCP Cloud DataFlow or Azure Synapse Analytics Spark Pools)  | Support for parallelizeable and distributed cost-optimized workloads of batch, microbatch and streaming nature. At the same time, it is a solution which can abide by proper programming standards using modularity, reuseability and consistency | Implentations are more time consuming and require increasingly expert knowledge. In summary: it is easier to find SQL then Spark developers. |Data/Analytics Engineer |
| Storage      | Delta/Iceberg in AWS S3, GCP Cloud Storage or Azure Blob Storage  | Horizontally scalable solutions allow for lost-cost high-volume analytics tightly integrated with Apache Spark, whilst providing automatic time-travel, auditing capabilities, ACID compliance, automated CDC, support for multiple pipeline types, among others | More complex and less matured solution  |Data/Analytics Engineer |
| Compute      | Apache Spark  (Databricks, AWS EMR/Glub, GCP Cloud DataFlow or Azure Synapse Analytics Spark Pools)      | Most vendors offer Serverless pools or Spot-instances, drastically lowering costs on a on-demand basis. At the same time, Spark offers integrated solutions for CI/CD when using Databricks, facilitating the monitoring and deployment process whilst leverating unit and integration tests. Spark can also be used to deploy ML instances and experimentations. Lastly, using Spark, instances can be selected according to the pipeline workload hence, further cost optimization can be achieved |  (see above) |Data/Analytics Engineer |
| Orchestration      | Apache Airflow, Dagster  | |  |Data/Analytics Engineer |
| Visualization      | Power BI, Tableau, SQL & Spark | allow for centralized data analysis & metadata handling, facilitating the process of establishing the Data Team as a single source of truth for the entire company, ensuring all stakeholders look at the same numbers and conceptsvia shared data models and metrics layers. The inclusion of Spark also allows for more complex analysis and distributed compute for heavier workloads and advanced algorithms | More complex solutions requiring a larger team to handle in addition to the increasing costs of per-seat based licenses | Data Analyst / Scientist |
| Data Quality      | Apache Spark (Great Expectations / Soda)      | Simple data quality layer which is easy to implement | Complex to setup |Data/Analytics Engineer |
| Data Catalog      | Databricks Unity, Azure Purview, etc      | Integrated & comprehensive data catalog available for the entire business | Requires manual input to feed the Lineage |Data/Analytics Engineer |