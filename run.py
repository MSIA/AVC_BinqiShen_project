import argparse
import logging.config
import pkg_resources

import yaml
import joblib

from src.add_application import ApplicationManager, create_db
from src.s3 import upload_file_to_s3, download_file_from_s3
from src.acquire import import_data, clean
from src.features import featurize, get_ohe_data
from src.model import train_model, evaluate
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logging.config.fileConfig(pkg_resources.resource_filename(__name__, "config/logging/local.conf"),
                          disable_existing_loggers=False)
logger = logging.getLogger('loan-application-pipeline')

if __name__ == '__main__':

    # Add parsers for both creating a database and adding applications to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    parser.add_argument('--config', default='config/config.yaml', help='Path to configuration file')
    subparsers = parser.add_subparsers(dest="subparser_name")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for uploading data to s3
    sb_upload = subparsers.add_parser("upload_file_to_s3", help="Upload raw data to s3")
    sb_upload.add_argument('--s3_path', default='s3://2021-msia423-shen-binqi/raw/application_data.csv',
                           help="S3 data path to the data")
    sb_upload.add_argument('--local_path', default='data/sample/application_data.csv',
                           help="local path to the data")

    # Sub-parser for downloading data from s3
    sb_upload = subparsers.add_parser("download_file_from_s3", help="Download raw data from s3")
    sb_upload.add_argument('--s3_path', default='s3://2021-msia423-shen-binqi/raw/application_data.csv',
                           help="S3 data path to the data")
    sb_upload.add_argument('--local_path', default='data/sample/application_data.csv',
                           help="local path to the data")

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--id", help="ID of loan applicant")
    sb_ingest.add_argument("--contract_type", help="Identification if loan is cash or revolving")
    sb_ingest.add_argument("--gender", help="Gender of the client")
    sb_ingest.add_argument("--own_car", help="Flag if the client owns a car")
    sb_ingest.add_argument("--own_realty", help="Flag if the client owns a house or flat")
    sb_ingest.add_argument("--num_children", help="Number of children the client has")
    sb_ingest.add_argument("--income_total", help="Income of the client")
    sb_ingest.add_argument("--amt_credit", help="Credit amount of the loan")
    sb_ingest.add_argument("--amt_annuity", help="Loan annuity")
    sb_ingest.add_argument("--amt_goods_price", help="Price of the goods for which the loan is given")
    sb_ingest.add_argument("--income_type", help="Clients income type (businessman, working, maternity leave)")
    sb_ingest.add_argument("--edu_type", help="Level of highest education the client achieved")
    sb_ingest.add_argument("--family_status", help="Family status of the client")
    sb_ingest.add_argument("--age", help="Client's age in days at the time of application")
    sb_ingest.add_argument("--years_employed", help="# days before the application one started current employment")
    sb_ingest.add_argument("--years_id_publish", help="# days before the application one change the identity document")
    sb_ingest.add_argument("--phone_contactable", help="Whether the client is reachable by the phone provided")
    sb_ingest.add_argument("--cnt_family_members", help="Number of family members does client have")
    sb_ingest.add_argument("--amt_req_credit_bureau_day", help="# enquiries to Credit Bureau about the client")
    sb_ingest.add_argument("--employed",  help="Flag if the client is employed")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/application.db',
                           help="SQLAlchemy Connection URI for database")

    # Sub-parser for acquiring data
    sb_acquire = subparsers.add_parser("run_model_pipeline",
                                       description="Acquire data, clean data, featurize data, and run model-pipeline")
    sb_acquire.add_argument('--s3_path', default='s3://2021-msia423-shen-binqi/raw/application_data.csv',
                            help="S3 data path to the data")
    sb_acquire.add_argument('--local_path', default='data/sample/application_data.csv',
                            help="local path to the data")

    args = parser.parse_args()
    sp_used = args.subparser_name

    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        am = ApplicationManager(engine_string=args.engine_string)
        am.add_application(args.id, args.target, args.contract_type,
                           args.gender, args.own_car, args.own_realty,
                           args.num_children, args.income_total,
                           args.amt_credit, args.amt_annuity,
                           args.amt_goods_price, args.income_type,
                           args.edu_type, args.family_status,
                           args.age, args.years_employed,
                           args.years_id_publish, args.phone_contactable,
                           args.cnt_family_members, args.amt_req_credit_bureau_day,
                           args.employed)
        am.close()
    elif sp_used == 'upload_file_to_s3':
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == 'download_file_from_s3':
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'run_model_pipeline':
        # load yaml configuration file
        with open(args.config, "r") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
        logger.info("Configuration file loaded from %s" % args.config)

        # download raw data from s3
        download_file_from_s3(args.local_path, args.s3_path)

        # model pipeline: clean -> featurize -> one-hot-encode -> model -> evaluation
        raw = import_data(args.local_path, **conf['acquire']['import_data'])
        cleaned = clean(raw, **conf['acquire']['clean'])
        featurized = featurize(cleaned, **conf['features']['featurize'])
        ohe_data = get_ohe_data(featurized, **conf['features']['get_ohe_data'])
        model_result = train_model(ohe_data, **conf['model']['train_model'])
        rf_mod = model_result[0]
        X_test = model_result[1]
        y_test = model_result[2]
        evaluate_result = evaluate(rf_mod, X_test, y_test)

        # save the trained model
        joblib.dump(rf_mod, conf['predict']['get_prediction']['model_path'])
        logger.info("Trained model save to location: %s", conf['predict']['get_prediction']['model_path'])
    else:
        parser.print_help()
