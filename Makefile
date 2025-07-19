run:
	cd src && uv run python app.py

run-wsgi:
	cd src && uv run gunicorn --bind 0.0.0.0:5000 --workers 1 wsgi:app