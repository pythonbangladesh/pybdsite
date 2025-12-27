import os
from flask import Flask, render_template, make_response, request, abort
from weasyprint import HTML
from flask import redirect

from utility import get_social_links
from utils_certificate import get_certificate_data

import structlog

app = Flask(__name__)
logger = structlog.get_logger("__name__")

@app.route('/')
def home():
    SOCIAL_LINKS = get_social_links()
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


@app.route('/certificate/<ref_code>')
def show_certificate(ref_code):
    try:
        data = get_certificate_data(ref_code)
        logger.info(f"Fetched certificate data for ref_code '{ref_code}'", context=data)
        context = {
            'event_id': data.get('event_id'),
            'participant_name': data.get('participant_name'),
            'score': data.get('score'),
            'certificate_id': data.get('certificate_id'),
            'event_name': data.get('event_name'),
            'event_type': data.get('event_type'),
            'event_sub_type': data.get('event_sub_type'),
            'facilitator': data.get('facilitator'),
            'director': data.get('director'),
            'organizer': data.get('Organizer') or "AI/ML Professional Community Bangladesh",
            'year': data.get('year'),
            'month': data.get('month'),
            'day': data.get('day'),
            'pdf_mode': True,
            'social_links': get_social_links()
        }
        return render_template('certificates/workshop_research_lifecycle.html', **context)
    
    except Exception as e:
        raise e

    except ValueError as e:
        # Invalid format or data integrity issues
        abort(400, description=str(e))
    
    except FileNotFoundError as e:
        # Certificate or event not found
        abort(404, description=str(e))
    
    except Exception as e:
        # Unexpected errors
        abort(500, description=f"Internal server error: {str(e)}")


@app.route('/certificate/<ref_code>/download')
def download_certificate(ref_code):
    try:
        data = get_certificate_data(ref_code)
        context = {
            'event_id': data.get('event_id'),
            'participant_name': data.get('participant_name'),
            'score': data.get('score'),
            'certificate_id': data.get('certificate_id'),
            'event_name': data.get('event_name'),
            'event_type': data.get('event_type'),
            'event_sub_type': data.get('event_sub_type'),
            'facilitator': data.get('facilitator'),
            'director': data.get('director'),
            'organizer': data.get('Organizer') or "AI/ML Professional Community Bangladesh",
            'year': data.get('year'),
            'month': data.get('month'),
            'day': data.get('day'),
            'pdf_mode': True,
        }
        html_content = render_template('certificates/workshop_research_lifecycle.html', **context)
        pdf = HTML(string=html_content, base_url=request.url_root).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=certificate_{ref_code}.pdf'
        return response
    
    except ValueError as e:
        abort(400, description=str(e))
    
    except FileNotFoundError as e:
        abort(404, description=str(e))
    
    except Exception as e:
        abort(500, description=f"Internal server error: {str(e)}")


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """
    Certificate verification endpoint.
    GET: Shows verification form
    POST: Processes verification and shows result
    """
    result = None
    social_links = get_social_links()
    if request.method == 'POST':
        category = request.form.get('community', '').strip()
        ref_code = request.form.get('cert_id', '').strip().upper()
        
        try:
            cert_data = get_certificate_data(ref_code)
            result = {
                'status': 'verified',
                'ref_code': ref_code,
                'data': cert_data
            }
        except (FileNotFoundError, ValueError) as e:
            result = {
                'status': 'not_found',
                'ref_code': ref_code,
                'error': str(e)
            }
        except Exception as e:
            result = {
                'status': 'error',
                'ref_code': ref_code,
                'error': 'System error occurred'
            }
    return render_template('partial/verify.html', result=result, social_links=social_links)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to 10000 for Render
    print(f"---------Starting app on port {port}-------------")
    app.run(debug=False, host='0.0.0.0', port=port)