from flask import Flask, render_template
from flask import redirect

import os


app = Flask(__name__)


@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/healthz')
def health():
    return "OK", 200


@app.route('/coc')
def coc():
    external_coc = 'https://github.com/pythonbangladesh/public-docs/blob/main/code-of-conduct.md'
    return redirect(external_coc)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to 10000 for Render
    print(f"---------Starting app on port {port}-------------")
    app.run(debug=False, host='0.0.0.0', port=port)