.PHONY: image image_app

image:
	docker build -f Dockerfile -t bse1248_application_data .

image_app:
	docker build -f app/Dockerfile -t bse1248_application .

.PHONY: upload_file_to_s3 download_file_from_s3
upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY bse1248_application_data run.py upload_file_to_s3

download_file_from_s3:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY bse1248_application_data run.py download_file_from_s3

.PHONY: create_db_local create_db_rds connect_db
create_db_local:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ bse1248_application_data run.py create_db

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME bse1248_application_data run.py create_db

connect_db:
	docker run -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}

.PHONY: raw cleaned featurized model test

raw: data/sample/application_data.csv

data/artifacts/cleaned.csv: download_file_from_s3
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ bse1248_application_data run.py run_model_pipeline --step clean --config=config/config.yaml --output=data/artifacts/cleaned.csv

cleaned: data/artifacts/cleaned.csv

data/artifacts/featurized.csv: data/artifacts/cleaned.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ bse1248_application_data run.py run_model_pipeline --step featurize --input=data/artifacts/cleaned.csv --config=config/config.yaml --output=data/artifacts/featurized.csv

featurized: data/artifacts/featurized.csv

models/randomforest.joblib: data/artifacts/featurized.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ bse1248_application_data run.py run_model_pipeline --step model --input=data/artifacts/featurized.csv --config=config/config.yaml --output=models/randomforest.joblib

model: models/randomforest.joblib

test:
	docker run -it bse1248_application_data run.py run_model_pipeline --step test

.PHONY: app

app:
	docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 bse1248_application python3 app.py
