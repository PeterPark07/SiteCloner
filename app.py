from flask import Flask, request, Response, render_template
from urllib.request import urlopen

app = Flask(__name__)

user_site = ""

@app.route('/clone/<path:site>')
def set_site(site):
    global user_site
    user_site = site
    return f"User site set to: {user_site}"

@app.route('/<path:url>')
def proxy(url):
    if not url:
        return 'good one '
    global user_site
    full_url = user_site + '/' + url
    try:
        response = urlopen(full_url)
        content_type = response.getheader('Content-Type')
        html_content = response.read()

        return Response(html_content, content_type=content_type)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
