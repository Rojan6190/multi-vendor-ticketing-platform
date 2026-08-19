.PHONY: up upd down build logs migrate makemigrations superuser shell test bash

up:                  ## run in foreground
	docker compose up

upd:                  ## run in background
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f web

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

test:
	docker compose exec web python manage.py test

bash:
	docker compose exec web sh