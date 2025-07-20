PYTHON = uv run python
run:
	$(PYTHON) src/app.py

run-prod:
	cd src && uv run gunicorn --bind 0.0.0.0:$${PORT:-10000} --workers 1 --timeout 60 app:app