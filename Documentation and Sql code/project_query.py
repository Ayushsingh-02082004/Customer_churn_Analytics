CREATE TABLE stg_zip_population (
    zip_code VARCHAR(10),
    population INT
);

SELECT current_database();


CREATE TABLE stg_customer_churn (
customer_id VARCHAR(20),
gender VARCHAR(10),
age INT,
married VARCHAR(10),
number_of_dependents INT,
city VARCHAR(100),
zip_code VARCHAR(10),
latitude DECIMAL(10,6),
longitude DECIMAL(10,6),
number_of_referrals INT,
tenure_in_months INT,
offer VARCHAR(20),
phone_service VARCHAR(10),
avg_monthly_long_distance_charges DECIMAL(10,2),
multiple_lines VARCHAR(10),
internet_service VARCHAR(10),
internet_type VARCHAR(30),
avg_monthly_gb_download INT,
online_security VARCHAR(10),
online_backup VARCHAR(10),
device_protection_plan VARCHAR(10),
premium_tech_support VARCHAR(10),
streaming_tv VARCHAR(10),
streaming_movies VARCHAR(10),
streaming_music VARCHAR(10),
unlimited_data VARCHAR(10),
contract VARCHAR(30),
paperless_billing VARCHAR(10),
payment_method VARCHAR(50),
monthly_charge DECIMAL(10,2),
total_charges DECIMAL(12,2),
total_refunds DECIMAL(12,2),
total_extra_data_charges DECIMAL(12,2),
total_long_distance_charges DECIMAL(12,2),
total_revenue DECIMAL(12,2),
customer_status VARCHAR(20),
churn_category VARCHAR(50),
churn_reason VARCHAR(255)
);

COPY stg_customer_churn
FROM 's3://telecom-redshift-assignment-ayush/raw/telecom_customer_churn.csv'
IAM_ROLE 'arn:aws:iam::890615325018:role/RedshiftS3AccessRole'
CSV
IGNOREHEADER 1;


COPY stg_zip_population
FROM 's3://telecom-redshift-assignment-ayush/raw/telecom_zipcode_population.csv'
IAM_ROLE 'arn:aws:iam::890615325018:role/RedshiftS3AccessRole'
CSV
IGNOREHEADER 1;

SELECT COUNT(*) FROM stg_customer_churn;

SELECT COUNT(*) FROM stg_zip_population;


CREATE TABLE customer_churn_analytics
DISTKEY(zip_code)
SORTKEY(customer_status, tenure_in_months)
AS
SELECT
    c.customer_id,
    c.city,
    c.zip_code,
    p.population,
    c.tenure_in_months,
    c.monthly_charge,
    c.total_charges,
    c.customer_status
FROM stg_customer_churn c
LEFT JOIN stg_zip_population p
ON c.zip_code = p.zip_code;

SELECT COUNT(*)
FROM customer_churn_analytics;

SELECT *
FROM customer_churn_analytics
LIMIT 10;


SELECT
    COUNT(*) AS total_customers,
    SUM(
        CASE
            WHEN customer_status = 'Churned' THEN 1
            ELSE 0
        END
    ) AS churned_customers,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN customer_status = 'Churned' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS churn_rate_percentage
FROM customer_churn_analytics;


SELECT
    city,
    COUNT(*) AS churned_customers
FROM customer_churn_analytics
WHERE customer_status = 'Churned'
GROUP BY city
ORDER BY churned_customers DESC
LIMIT 10;


SELECT
    CASE
        WHEN tenure_in_months BETWEEN 0 AND 12 THEN '0-12 Months'
        WHEN tenure_in_months BETWEEN 13 AND 24 THEN '13-24 Months'
        WHEN tenure_in_months BETWEEN 25 AND 48 THEN '25-48 Months'
        ELSE '49+ Months'
    END AS tenure_group,
    COUNT(*) AS churned_customers
FROM customer_churn_analytics
WHERE customer_status = 'Churned'
GROUP BY 1
ORDER BY 1;


SELECT
    ROUND(SUM(total_revenue),2) AS revenue_lost_due_to_churn
FROM stg_customer_churn
WHERE customer_status = 'Churned';



SELECT
    zip_code,
    population,
    COUNT(customer_id) AS customer_count
FROM customer_churn_analytics
GROUP BY
    zip_code,
    population
ORDER BY customer_count DESC
LIMIT 20;


ANALYZE customer_churn_analytics;

ANALYZE stg_customer_churn;
ANALYZE stg_zip_population;


VACUUM customer_churn_analytics;