import logging.config

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()


class Application(Base):
    """Create a data model for the database for capturing loan applicants information
    """

    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    target = Column(Integer, unique=False, nullable=True)
    contract_type = Column(String(100), unique=False, nullable=True)
    gender = Column(String(100), unique=False, nullable=True)
    own_car = Column(String(100), unique=False, nullable=True)
    own_realty = Column(String(100), unique=False, nullable=True)
    num_children = Column(Integer, unique=False, nullable=True)
    income_total = Column(Float, unique=False, nullable=True)
    amt_credit = Column(Float, unique=False, nullable=True)
    amt_annuity = Column(Float, unique=False, nullable=True)
    amt_goods_price = Column(Float, unique=False, nullable=True)
    income_type = Column(String(100), unique=False, nullable=True)
    edu_type = Column(String(100), unique=False, nullable=True)
    family_status = Column(String(100), unique=False, nullable=True)
    days_birth = Column(Integer, unique=False, nullable=True)
    days_employed = Column(Integer, unique=False, nullable=True)
    days_id_change = Column(Integer, unique=False, nullable=True)
    phone_contactable = Column(Integer, unique=False, nullable=True)
    cnt_family_members = Column(Integer, unique=False, nullable=True)
    amt_req_credit_bureau_day = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<Track %r>' % self.title


def create_db(engine_string: str):
    """Create a database from provided engine string

    Args:
        engine_string (str): Engine string

    Returns:
        None

    """
    engine = sqlalchemy.create_engine(engine_string)

    Base.metadata.create_all(engine)
    logger.info("Database created.")


class ApplicationManager:

    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app (Flask): Flask app
            engine_string (str): Engine string
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self):
        """Closes SQLAlchemy session

        Returns:
            None

        """
        self.session.close()

    def add_application(self, id: int, target: int, contract_type: str,
                        gender: str, own_car: str, own_realty: str,
                        num_children: int, income_total: float,
                        amt_credit: float, amt_annuity: float,
                        amt_goods_price: float, income_type: str,
                        edu_type: str, family_status: str,
                        days_birth: int, days_employed: int,
                        days_id_change: int, phone_contactable: int,
                        cnt_family_members: int, amt_req_credit_bureau_day: int):
        """Seeds an existing database with additional applications.

        Args:
            id (int): ID of loan in the sample
            target (int): Target variable (1: client with payment difficulties; 0: all other cases)
            contract_type (str): Identification if loan is cash or revolving
            gender (str): Gender of the client
            own_car (str): Flag if the client owns a car
            own_realty (str): Flag if client owns a house or flat
            num_children (int): Number of children the client has
            income_total (float): Income of the client
            amt_credit (float): Credit amount of the loan
            amt_annuity (float): Loan annuity
            amt_goods_price (float): price of the goods for which the loan is given
            income_type (str): Clients income type
            edu_type (str): Level of highest education the client achieved
            family_status (str): Family status of the client
            days_birth (int): Client's age in days at the time of application
            days_employed (int): Number of days before the application the person started current employment
            days_id_change (int): Number of days before the application did client change the identity document
            phone_contactable (int): Whether the phone provided is reachable
            cnt_family_members (int): Number of family members does client have
            amt_req_credit_bureau_day (int): Number of enquiries to Credit Bureau about the client

        Returns:
            None

        """
        session = self.session
        applicant = Application(id=id,
                                target=target,
                                contract_type=contract_type,
                                gender=gender,
                                own_car=own_car,
                                own_realty=own_realty,
                                num_children=num_children,
                                income_total=income_total,
                                amt_credit=amt_credit,
                                amt_annuity=amt_annuity,
                                amt_goods_price=amt_goods_price,
                                income_type=income_type,
                                edu_type=edu_type,
                                family_status=family_status,
                                days_birth=days_birth,
                                days_employed=days_employed,
                                days_id_change=days_id_change,
                                phone_contactable=phone_contactable,
                                cnt_family_members=cnt_family_members,
                                amt_req_credit_bureau_day=amt_req_credit_bureau_day)
        session.add(applicant)
        session.commit()
        logger.info("Customer # %s added to database", id)
