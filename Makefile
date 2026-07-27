.PHONY: up down clean install setup-airflow abctl-up help

help:
	@echo "Available commands:"
	@echo "  make up          - Start the Docker infrastructure (Airflow & Spark)"
	@echo "  make down        - Stop the Docker infrastructure"
	@echo "  make clean       - Stop containers and remove all local data"

up:
	docker-compose up -d
	@echo "Airflow and Spark are up! Give it a moment to initialize."
	@echo "Airflow UI: http://localhost:8080 (airflow/airflow)"

down:
	docker-compose down -v

clean:
	docker-compose down -v
	rm -rf data/source/* data/bronze/* data/silver/* data/gold/*
	@echo "Cleaned all data and removed containers."
