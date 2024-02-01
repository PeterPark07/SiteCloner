from flask import Flask, request, Response
from urllib.request import urlopen

app = Flask(__name__)

user_site = ""

js_code = """
<script>
    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('click', e => {
            const targetUrl = e.target.getAttribute('href');
            if (targetUrl && targetUrl.startsWith('http') && !window.confirm('You are leaving the proxy site. Continue?')) {
                e.preventDefault();
            }
        });
    });
</script>
"""

@app.route('/clone/<path:site>')
def set_site(site):
    global user_site
    user_site = site
    return f"User site set to: {user_site}"

def fetch_and_modify_content(url):
    global user_site
    full_url = user_site + '/' + url
    try:
        response = urlopen(full_url)
        content_type = response.getheader('Content-Type')
        html_content = response.read()
        return html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1), content_type
    except Exception as e:
        return str(e), 'text/plain'

@app.route('/<path:url>')
def proxy(url):
    modified_content, content_type = fetch_and_modify_content(url)
    return Response(modified_content, content_type=content_type)

@app.route('/')
def site():
    modified_content, content_type = fetch_and_modify_content('')
    return Response(modified_content, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
