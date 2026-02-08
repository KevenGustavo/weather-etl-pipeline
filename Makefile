# Makefile para Weather ETL Pipeline

.PHONY: up down logs clean help

help:
	@echo "Comandos disponíveis:"
	@echo "  make up    - Sobe todo o ambiente (build + start)"
	@echo "  make down  - Para e remove os containers"
	@echo "  make logs  - Vê os logs do ETL em tempo real"
	@echo "  make clean - Limpa arquivos temporários (__pycache__)"

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f etl_pipeline

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +