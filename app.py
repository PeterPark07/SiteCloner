from flask import Flask, request, Response

app = Flask(__name__)

user_site = ""

js_code = """
<script>
    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('click', e => {
            const targetUrl = e.target.getAttribute('href');
            if (targetUrl && targetUrl.startsWith('http') && !window.confirm('You are leaving the proxy site and going to ' + targetUrl + '. Continue?')) {
                e.preventDefault();
            }
        });
    });
</script>
"""

@app.route('/clone', methods=['GET', 'POST'])
def clone_site():
    global user_site
    if request.method == 'POST':
        site = request.form.get('site', '')
        user_site = site
        return f"User site set to: {user_site}"
    return """
    <form method="post">
        <label for="site">Enter Website URL:</label>
        <input type="text" id="site" name="site">
        <input type="submit" value="Clone">
    </form>
    """

def fetch_and_modify_content(url):
    global user_site
    full_url = user_site + '/' + url
    try:
        response = requests.get(full_url)
        content_type = response.headers['Content-Type']
        html_content = response.content
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
