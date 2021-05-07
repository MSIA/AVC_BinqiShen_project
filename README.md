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
  * [2. Load data into S3](#2-load-data-into-s3)
    + [AWS Credentials Configuration](#aws-credentials-configuration)
    + [Load data into S3](#load-data-into-s3)
  * [3. Initialize the database](#3-initialize-the-database)
    + [Configure Environment Variables](#configure-environment-variables)
    + [Create the Database on RDS](#create-the-database-on-rds)
    + [Create the Database Locally](#create-the-database-locally)
    
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
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
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
│   ├──add_application.py             <- Python script that adds data and creates database
│   ├──s3.py                          <- Python script that connects to S3
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app

*Note: Please be sure to be connected to the Northwestern VPN and go to the root directory of the repository before you move forward with the following steps.*


### 1. Build the Docker Image 
*Note: Please be sure your Docker Desktop is open before you move forward with the following steps*

`docker build -f app/Dockerfile -t application_data .`


### 2. Load data into S3

#### AWS Credentials Configuration
To configure AWS credentials, run the following commends in terminal to load your credentials as environment variables: 
*Note: Please remember to change the "YOUR_ACCESS_KEY_ID" and "YOUR_SECRET_ACCESS_KEY" below to your own AWS credentials*

`export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"`

`export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"`


#### Load data into S3
The data used for this project was obtained from this [Credit Card Fraud Detection](https://www.kaggle.com/mishra5001/credit-card) Kaggle dataset. Since the data i relatively small, there is a copy of the loan application data in this repository with the following path: `data/sample/application_data.csv`. 

Run the following commend to load data to S3: 

```
docker run \
   -e AWS_ACCESS_KEY_ID \
   -e AWS_SECRET_ACCESS_KEY \
   application_data src/s3.py --local_path={local_file_path} --s3_path={s3_file_path}
```

### 3. Initialize the database 

#### Configure Environment Variables

To configure the `.mysqlconfig` file, run: `vi .mysqlconfig` in terminal. 

Press `I` to enter the "Insert" mode and change the following variables to match your credentials. 

- `MYSQL_USER` = "YOUR_RDS_USERNAME"
- `MYSQL_PASSWORD` = "YOUR_RDS_PASSWORD"
- `MYSQL_HOST` = "YOUR_RDS_HOST_ENDPOINT"
- `MYSQL_PORT` = 3306 
- `DATABASE_NAME` = msia423_db

After done with the above, press `esc`, type `wq`, and press `return` on your keyboard to save the changes.

Type the following commend in your terminal to update the .mysqlconfig file: `source .mysqlconfig`

#### Create the Database on RDS

To create the database on RDS, run the following commend in your terminal: 

```
docker run -it \
    -e MYSQL_HOST \
    -e MYSQL_PORT \
    -e MYSQL_USER \
    -e MYSQL_PASSWORD \
    -e DATABASE_NAME \
    application run.py create_db
```

#### Create the Database Locally

To create the database locally, you can run the following commend: `docker run -it application_data run.py create_db`

You may configure the `Engine String` using the following commend in your terminal: 

`export SQLALCHEMY_DATABASE_URI = "YOUR_ENGINE_STRING"`

`docker run -it -e SQLALCHEMY_DATABASE_URI application_data run.py create_db`

You may also use the following commend: `python run.py create_db` to create the local SQLite database at `sqlite:///data/application.db`. 

