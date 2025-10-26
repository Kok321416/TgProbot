# TgProbot Makefile
# Упрощенные команды для разработки и деплоя

.PHONY: help install test lint format build run stop clean deploy setup

# Переменные
DOCKER_IMAGE = tgprobot
DOCKER_TAG = latest
CONTAINER_NAME = tgprobot

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

test: ## Запустить тесты
	pytest tests/ -v --cov=. --cov-report=html

lint: ## Проверить код линтером
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Форматировать код
	black .

format-check: ## Проверить форматирование
	black --check --diff .

build: ## Собрать Docker образ
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

run: ## Запустить бота локально
	docker-compose up -d

stop: ## Остановить бота
	docker-compose down

logs: ## Показать логи
	docker-compose logs -f

shell: ## Войти в контейнер
	docker-compose exec $(CONTAINER_NAME) /bin/bash

clean: ## Очистить Docker ресурсы
	docker-compose down -v
	docker system prune -f
	docker image prune -f

deploy: ## Деплой на сервер
	@echo "Деплой на сервер..."
	ssh deploy@your-server.com "cd /opt/tgprobot && git pull && ./scripts/deploy.sh"

setup: ## Первоначальная настройка
	@echo "Настройка проекта..."
	cp env.production.example .env
	@echo "Отредактируйте файл .env с вашими настройками"
	@echo "Запустите 'make install' для установки зависимостей"

dev: ## Запуск в режиме разработки
	python main.py

debug: ## Запуск диагностики email
	python debug_email.py

status: ## Показать статус
	docker-compose ps

restart: ## Перезапустить бота
	docker-compose restart

update: ## Обновить зависимости
	pip install --upgrade -r requirements.txt

backup: ## Создать бэкап
	@echo "Создание бэкапа..."
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz . --exclude=venv --exclude=.git

# Команды для CI/CD
ci-test: install lint format-check test

ci-build: build

ci-deploy: deploy
