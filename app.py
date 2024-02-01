from flask import Flask, request, Response
from urllib.request import urlopen

app = Flask(__name__)

user_site = ""

# JavaScript code to display a confirmation dialog for external links
js_code = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        var links = document.getElementsByTagName('a');
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener('click', function(e) {
                var targetUrl = this.getAttribute('href');
                if (!targetUrl.startsWith('{user_site}') && 
                    !targetUrl.startsWith('http') && 
                    targetUrl.indexOf('.') !== -1) {
                    e.preventDefault();
                    var confirmed = window.confirm('You are leaving the proxy site. Continue?');
                    if (confirmed) {
                        window.location.href = targetUrl;
                    }
                }
            });
        }
    });
</script>
"""

@app.route('/clone/<path:site>')
def set_site(site):
    global user_site
    user_site = site
    return f"User site set to: {user_site}"

@app.route('/<path:url>')
def proxy(url):
    global user_site
    full_url = user_site + '/' + url
    try:
        response = urlopen(full_url)
        content_type = response.getheader('Content-Type')
        html_content = response.read()

        # Inject JavaScript code into the HTML content
        html_content = html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1)

        return Response(html_content, content_type=content_type)
    except Exception as e:
        return str(e)

@app.route('/')
def site():
    global user_site
    try:
        response = urlopen(user_site)
        content_type = response.getheader('Content-Type')
        html_content = response.read()

        # Inject JavaScript code into the HTML content
        html_content = html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1)

        return Response(html_content, content_type=content_type)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
