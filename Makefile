image:
	docker build -f Dockerfile -t application_data .

upload_file_to_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY application_data run.py upload_file_to_s3

download_file_from_s3:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY application_data run.py download_file_from_s3

create_db_local:
	docker run -it application_data run.py create_db

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME application_data run.py create_db

connect_db:
	docker run -it --rm mysql:5.7.33 mysql -h$$MYSQL_HOST -u$$MYSQL_USER -p$$MYSQL_PASSWORD

model:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY application_data run.py run_model_pipeline

test:
	docker run -it application_data run.py test

app:
	docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME -p 5000:5000 application_data app.py

.PHONY: image upload_file_to_s3 download_file_from_s3 create_db_local create_db_rds connect_db model test app
