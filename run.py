import argparse
import logging.config

from src.add_application import ApplicationManager, create_db
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('loan-application-pipeline')


if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--id", help="ID of loan in the sample")
    sb_ingest.add_argument("--target", help="Target variable (1 indicates client with payment difficulties)")
    sb_ingest.add_argument("--contract_type", help="Identification if loan is cash or revolving")
    sb_ingest.add_argument("--gender", help="Gender of the client")
    sb_ingest.add_argument("--own_car", help="Flag if the client owns a car")
    sb_ingest.add_argument("--own_realty", help="Flag if client owns a house or flat")
    sb_ingest.add_argument("--num_children", help="Number of children the client has")
    sb_ingest.add_argument("--income_total", help="Income of the client")
    sb_ingest.add_argument("--amt_credit", help="Credit amount of the loan")
    sb_ingest.add_argument("--amt_annuity", help="Loan annuity")
    sb_ingest.add_argument("--amt_goods_price", help="Price of the goods for which the loan is given")
    sb_ingest.add_argument("--income_type", help="Clients income type (businessman, working, maternity leave)")
    sb_ingest.add_argument("--edu_type", help="Level of highest education the client achieved")
    sb_ingest.add_argument("--family_status", help="Family status of the client")
    sb_ingest.add_argument("--days_birth", help="Client's age in days at the time of application")
    sb_ingest.add_argument("--days_employed", help="# days before the application one started current employment")
    sb_ingest.add_argument("--days_id_change", help="# days before the application one change the identity document")
    sb_ingest.add_argument("--phone_contactable", help="Whether the client is reachable by the phone provided")
    sb_ingest.add_argument("--cnt_family_members", help="Number of family members does client have")
    sb_ingest.add_argument("--amt_req_credit_bureau_day", help="# enquiries to Credit Bureau about the client")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        tm = ApplicationManager(engine_string=args.engine_string)
        tm.add_track(args.id, args.target, args.contract_type,
                     args.gender, args.own_car, args.own_realty,
                     args.num_children, args.income_total,
                     args.amt_credit, args.amt_annuity,
                     args.amt_goods_price, args.income_type,
                     args.edu_type, args.family_status,
                     args.days_birth, args.days_employed,
                     args.days_id_change, args.phone_contactable,
                     args.cnt_family_members, args.amt_req_credit_bureau_day)
        tm.close()
    else:
        parser.print_help()



