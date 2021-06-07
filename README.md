# Avoiding Delinquency in Loan Payments

Project Developer: Binqi Shen

QA support: Yijun Wu

<!-- toc -->

## Table of Contents 

- [Project Charter](#project-charter)
  * [Vision](#vision)
  * [Mission](#mission)
  * [Success Criteria](#success-criteria)
- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Build the Docker Image](#1-build-the-docker-image)
  * [2. Load data into S3 and Download data from S3](#2-load-data-into-s3-and-download-data-from-s3)
    + [AWS Credentials Configuration](#aws-credentials-configuration)
    + [Load data into S3](#load-data-into-s3)
    + [Download data from S3](#download-data-from-s3)
  * [3. Initialize the database](#3-initialize-the-database)
    + [Create the Database Locally](#create-the-database-locally)
    + [Configure Environment Variables](#configure-environment-variables)
    + [Create the Database on RDS](#create-the-database-on-rds)
    + [Test Connection to Database](#test-connection-to-database)
  * [4. Model Pipeline](#4-model-pipeline)
  * [5. Running the Flask App](#5-running-the-flask-app)
  * [6. Testing](6-testing)

    
<!-- tocstop -->

## Project Charter

### Vision 

Loan payment delinquency happens when the borrower fails to make scheduled payments as both parties agreed upon at first. Late loan payments could have serious adverse consequences for both the borrowers and the lenders. For loan borrowers, delinquent loan payments would not only lead to higher penalty fees, but also have negative impacts on their credit scores, which could severely affect their ability to borrow in the future. On the other hand, loan lenders suffer from being subject to the higher risk of not being able to receive the money as scheduled and the borrower might fail to make payments for more than one payment period. 

With the intention of promoting a financially healthier loan market, this app helps both the loan borrowers and the lenders identify the possibility of loan payment delinquency, even before issuing any loans. If there is a high possibility of delinquent payment, the lender should reconsider the terms and conditions of the loans for the borrower. At the same time, the borrower should reconsider the amount he/she is borrowing. 

### Mission 

The app gives the prediction of whether a loan borrower with certain attributes faces payment delinquency risks. In order to achieve the purpose of this app, a supervised classification algorithm will be leveraged along with the most important attributes of loan borrowers. The data used for this project was obtained from this [Credit Card Fraud Detection](https://www.kaggle.com/mishra5001/credit-card) dataset.

A typical user of the app will be asked to answer a series of questions regarding the attributes of the borrower (potential attributes include total income, education level, family status, etc.). With the user input, the App is going to output the probability of delinquency payment, which can be used to make decisions on whether a payment reminder is needed or whether a new loan should be issued. 

### Success criteria 

*Model Performance Metrics*

- The AUC (Area Under Curve) score will be one of the main model performance metrics because it works well with imbalanced datasets. An AUC of 70% would indicate that the model has good performance and is ready to be deployed in the app. The exact threshold may be negotiated later on.  
- CCR (Correct Classification Rate) score is another crucial model performance metric. It gives a proxy of the model accuracy by dividing the number of correctly classified observations by the total number of observations. The targeted CCR score for the model deployment is 70%. 

*Business Metrics*

- The monthly loan delinquency rate will be an important business metric here. Through A/B testing, we will be able to see whether following the app’s guidance on granting loans would lower the monthly delinquency rate compared to the results of not following the guidance of the app. 
- Another crucial business metric is the annual revenue earned by the loan lenders. As the loan market becomes financially healthier, we would expect the loan lenders to receive regular payments and have customers (borrowers) with higher credit scores. Hence the annual revenue will be an essential metric to estimate the business impact to the lenders. 

## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to acquire data, land data in s3, create table in RDS, and run model pipeline
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│   ├──acquire.py                     <- Python script that acquires and cleans data
│   ├──add_application.py             <- Python script that defines the data model for my table in RDS
│   ├──features.py                    <- Python script that generate new features from data
│   ├──model.py                       <- Python script that trains and evaluate a model (Random Forest Classifier)
│   ├──predict.py                     <- Python script that makes prediction for new user input
│   ├──s3.py                          <- Python script that connects to S3
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│   ├──test_acquire.py                <- Python script that tests the functions in acquire.py
│   ├──test_features.py               <- Python script that tests the functions in features.py
│   ├──test_predict.py                <- Python script that tests the functions in predict.py
│   ├──test_s3.py                     <- Python script that tests the functions in s3.py
│
├── Dockerfile                        <- Dockerfile for running the app
├── Makefile                          <- Makefile that contains shortcuts to terminal commands
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app

*Note: Please be sure to be **connected to the Northwestern VPN** and go to the **root directory** of the repository before you move forward with the following steps.*


### 1. Build the Docker Image 
*Note: Please be sure your Docker Desktop is open before you move forward with the following steps*

In order to acquire data, land data into S3, download data from S3, create table in RDS, and run the model pipeline, please run one of the following commands to build the docker image.
- Method 1: `make image`
- Method 2: `docker build -f Dockerfile -t application_data .`
 

### 2. Load data into S3 and Download data from S3

#### AWS Credentials Configuration
To configure AWS credentials, run the following commands in terminal to load your credentials as environment variables: 
*Note: Please remember to change the "YOUR_ACCESS_KEY_ID" and "YOUR_SECRET_ACCESS_KEY" below to your own AWS credentials*

`export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"`

`export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"`


#### Load data into S3
The data used for this project was obtained from this [Credit Card Fraud Detection](https://www.kaggle.com/mishra5001/credit-card) Kaggle dataset. Since the data is relatively small, there is a copy of the loan application data in this repository with the following path: `data/sample/application_data.csv`. 

Run the following command to load data to S3: 

```
docker run \
   -e AWS_ACCESS_KEY_ID \
   -e AWS_SECRET_ACCESS_KEY \
   application_data run.py upload_file_to_s3 \
   --local_path <local_file_path> \                  
   --s3_path <s3_file_path> 
```

Without specifying `--local_path` and `s3_path`, the default local path is: `data/sample/application_data.csv` and the default s3 path is: `s3://2021-msia423-shen-binqi/raw/application_data.csv`. 

If you want to upload data from a different local path, specify by adding the following: `--local_path <local_file_path>`

If you want to upload data to a different S3 path, specify by adding the following: `--s3_path <s3_file_path>`

#### Download data from S3
If you would like to download the datase used for this project from S3, please run the following commands: 

```
docker run \
    --mount type=bind,source="$(shell pwd)",target=/app/ \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    application_data run.py download_file_from_s3 \
    --local_path <local_file_path> \                  
    --s3_path <s3_file_path> 
```

Without specifying `--local_path` and `s3_path`, the default local path is: `data/sample/application_data.csv` and the default s3 path is: `s3://2021-msia423-shen-binqi/raw/application_data.csv`. 

If you want to upload data from a different local path, specify by adding the following: `--local_path <local_file_path>`

If you want to upload data to a different S3 path, specify by adding the following: `--s3_path <s3_file_path>`


### 3. Initialize the database 

#### Create the Database Locally

To create the database locally, you can run the following command: 

`docker run -it application_data run.py create_db`

The default Engine String is: `sqlite:///data/application.db`. You may also configure the `Engine String` through using the following 2 methods in your terminal: 

- Method 1: specify the '--engine_string' argument

`docker run -it application_data run.py create_db --engine_string <YOUR_ENGINE_STRING>`

- Method 2: set environment variable 'SQLALCHEMY_DATABASE_URI'

`export SQLALCHEMY_DATABASE_URI = "YOUR_ENGINE_STRING"`

`docker run -it -e SQLALCHEMY_DATABASE_URI application_data run.py create_db`


#### Configure Environment Variables 

This step is to prepare for creating the database on RDS.

To configure the `.mysqlconfig` file, run: `vi .mysqlconfig` in terminal. 

Press `I` to enter the "Insert" mode and change the following variables to match your credentials. 

- `MYSQL_USER` = "YOUR_RDS_USERNAME"
- `MYSQL_PASSWORD` = "YOUR_RDS_PASSWORD"
- `MYSQL_HOST` = "YOUR_RDS_HOST_ENDPOINT"
- `MYSQL_PORT` = "YOUR_PORT"
- `DATABASE_NAME` = "YOUR_DATABASE"

After done with the above, press `esc`, type `wq`, and press `return` on your keyboard to save the changes.

Type the following command in your terminal to update the .mysqlconfig file: `source .mysqlconfig`

#### Create the Database on RDS

To initialize an empty database on RDS, run one of the following commands in your terminal: 

- Method 1: 
 
`make create_db_rds`

- Method 2: 

```
docker run -it \
    -e MYSQL_HOST \
    -e MYSQL_PORT \
    -e MYSQL_USER \
    -e MYSQL_PASSWORD \
    -e DATABASE_NAME \
    application_data run.py create_db
```

Please note that if you choose to initialize an empty database on RDS, you would not be able to see the previous records that are already in the database. 

#### Test Connection to Database 

To test if you can connect to the database, run one of the following commands: 

- Method 1:

`make connect_db`

- Method 2:
```
docker run -it --rm \
    mysql:5.7.33 \
    mysql \
    -h$MYSQL_HOST \
    -u$MYSQL_USER \
    -p$MYSQL_PASSWORD
```

If successfully connected, you may run the following commands: 

- To show all the databases: `show databases;`
- To use a particular database: `use <database_name>;`
- After selecting a database, you can see al the tables in it by running: `show tables;`
- You may check the columns within a table by running: `show columns from <table_name>;`


### 4. Model Pipeline

A Random Forest Classifier was built to make predictions on loan delinquency for new applicants. The pretrained model is located in this repository with the following path: `models/randomforest.joblib`. 

If you wish to re-run the model pipeline, please run one of the following commands: 

- Method 1: 
 
`make model`

- Method 2: 

```
docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY application_data run.py run_model_pipeline
```

The resulting model would be stored in the following location: `models/randomforest.joblib`. 


### 5. Running the Flask App

To run the Flask app, run: 

`python app.py`

If you wish to run the Flask App in Docker, you need to first build docker image by running: 

`docker build -f app/Dockerfile -t application_data .`

Then you can run the following command to run this app using the following command: 
`docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME -p 5000:5000 application_data app.py`

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.


### 6. Testing

Unit test is run for src/acquire.py, src/features.py, src/predict.py, and src/s3.py. One "happy path" and one "unhappy path" per function would tested. 

- From within the Docker container, the following command should work to run unit tests when run from the root of the repository:

  - `python -m pytest`

- If you wish to run the unit tests using docker, please be sure that you have built the image by running either `make image` or `docker build -f Dockerfile -t application_data .` from the root of this repository. Then, run one of the following commands: 

  - `make test`
  - `docker run -it application_data run.py test`
