run: ## Run the test server.
	python manage.py runserver_plus

migrate: ## Apply migrations.
	python manage.py migrate

install: ## Install the python requirements.
	pip install -r requirements.txt
