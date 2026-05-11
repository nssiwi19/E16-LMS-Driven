.PHONY: install dev migrate seed test clean

install:
	pip install -r requirements.txt
	if [ ! -f .env ]; then cp .env.example .env; fi

dev:
	flask run --debug

migrate:
	flask db upgrade

seed:
	@echo "Seeding database... (Requires admin login & dev mode)"
	@echo "Login as admin and visit /admin/seed"

test:
	pytest

clean:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
