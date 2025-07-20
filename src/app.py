from flask import Flask, render_template
from flask import redirect

import os


app = Flask(__name__)


@app.route('/')
def home():
    SOCIAL_LINKS = {
        'linkedin': 'https://www.linkedin.com/company/python-bangladesh/',
        'discord': 'https://discord.gg/sR52eYRFba', 
        'whatsapp': 'https://whatsapp.com/channel/0029VbAf0s70rGiMzJfG4u2B',
        'github': 'https://github.com/pythonbangladesh'
    }
    try:
        return render_template('index.html', social_links=SOCIAL_LINKS)
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