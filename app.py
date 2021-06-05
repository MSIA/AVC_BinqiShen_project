import traceback
import logging.config

import yaml
from flask import Flask
from flask import render_template, request

from config.flaskconfig import CONTRACT_TYPE, GENDERS, BINARY, INCOME_TYPE, EDU_TYPE, FAM_STATUS
from src.add_application import Application, ApplicationManager
from src.predict import transform_input, get_prediction

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
application_manager = ApplicationManager(app)

# load yaml configuration file
with open('config/config.yaml', "r") as file:
    conf = yaml.load(file, Loader=yaml.FullLoader)
logger.info("Configuration file loaded")


@app.route('/')
def index():
    """Main view of the loan application that allows user input applicant information

    Create view into index page that allows users input applicant information

    Returns:
        rendered html template located at: app/templates/index.html

    """

    try:
        applications = application_manager.session.query(Application).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html', applications=applications, contract_type=CONTRACT_TYPE,
                               genders=GENDERS, own_car=BINARY, own_realty=BINARY,
                               income_type=INCOME_TYPE, edu_type=EDU_TYPE, fam_status=FAM_STATUS,
                               phone_contact=BINARY, employed=BINARY)
    except:
        traceback.print_exc()
        logger.warning("Not able to display loan applications information, error page returned")
        return render_template('error.html')


@app.route('/result', methods=['POST', 'GET'])
def add_entry():
    """View that process a POST with new applicant input

    Add new applicant information to Applications database and get prediction results

    Returns:
        rendered html template located at: app/templates/result.html if successfully processed,
        rendered html template located at: app/templates/error.html if any error occurs

    """
    if request.method == 'GET':
        return "Visit the homepage to add applicants and get predictions"
    elif request.method == 'POST':
        try:
            # Add new applicant information to RDS for future usages
            application_manager.add_application(
                contract_type=request.form['contract_type'],
                gender=request.form['gender'],
                own_car=request.form['own_car'],
                own_realty=request.form['own_realty'],
                num_children=request.form['num_children'],
                income_total=request.form['income_total'],
                amt_credit=request.form['amt_credit'],
                amt_annuity=request.form['amt_annuity'],
                amt_goods_price=request.form['amt_goods_price'],
                income_type=request.form['income_type'],
                edu_type=request.form['edu_type'],
                family_status=request.form['family_status'],
                age=request.form['age'],
                years_employed=request.form['years_employed'],
                years_id_publish=request.form['years_id_publish'],
                phone_contactable=request.form['phone_contactable'],
                cnt_family_members=request.form['cnt_family_members'],
                amt_req_credit_bureau_day=request.form['amt_req_credit_bureau_day'],
                employed=request.form['employed']
            )

            logger.info(
                "New applicant of contract type %s added",
                request.form['contract_type']
            )

            # Get loan delinquency prediction for the new applicant
            user_input = {'contract_type': request.form['contract_type'], 'gender': request.form['gender'],
                          'own_car': request.form['own_car'], 'own_realty': request.form['own_realty'],
                          'num_children': request.form['num_children'], 'income_total': request.form['income_total'],
                          'amt_credit': request.form['amt_credit'], 'amt_annuity': request.form['amt_annuity'],
                          'amt_goods_price': request.form['amt_goods_price'], 'income_type': request.form['income_type'],
                          'edu_type': request.form['edu_type'], 'family_status': request.form['family_status'],
                          'Age': request.form['age'], 'Years_Employed': request.form['years_employed'],
                          'Years_ID_Publish': request.form['years_id_publish'],
                          'phone_contactable': request.form['phone_contactable'],
                          'cnt_family_members': request.form['cnt_family_members'],
                          'amt_req_credit_bureau_day': request.form['amt_req_credit_bureau_day'],
                          'Employed': request.form['employed']}
            user_input_transformed = transform_input(user_input, **conf['predict']['transform_input'])
            user_prob = get_prediction(user_input_transformed, **conf['predict']['get_prediction'])[0]
            user_bin = get_prediction(user_input_transformed, **conf['predict']['get_prediction'])[1]

            logger.info(
                "The new applicant's probability of loan delinquency is: %f percent, "
                "hence %s", user_prob, user_bin
            )

            logger.debug("Result page accessed")
            return render_template('result.html', user_prob=user_prob, user_bin=user_bin)
        except:
            logger.warning("Not able to process your request, error page returned")
            return render_template('error.html')


@app.route('/about', methods=['GET'])
def about():
    """View of an 'About' page that has detailed information about the project

    Returns:
        rendered html template located at: app/templates/about.html

    """
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
