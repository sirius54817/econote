# econote

Econote is a small Flask-based e-commerce demo application that demonstrates
products, shopping cart, subscriptions, and simple admin/auth flows.

This repository contains the application source under the `app/` package and
an SQLite database used for development.

Quick start
1. Create and activate a virtual environment:

	python -m venv .venv
	source .venv/bin/activate

2. Install dependencies:

	pip install -r requirements.txt

3. Run the app locally:

	python run.py

By default the app will use the local SQLite database files in `app/site.db`
or `instance/app.db` for development.

Notes
- This project is intended for learning and demo purposes and is not
  production hardened.

Contributing
- Feel free to open issues or pull requests.

Contact
- Maintainer: sirius54817
