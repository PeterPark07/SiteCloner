from flask import Flask, request, Response
import requests
import time
import os

app = Flask(__name__)
server_url = os.getenv('url')

user_site = ""
js_code = """
<script>
    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('click', e => {
            const targetUrl = e.target.getAttribute('href');
            const isExternalLink = targetUrl && targetUrl.startsWith('http') && !targetUrl.startsWith({server_url});
            
            if (isExternalLink && !window.confirm('You are leaving the proxy site and going to ' + targetUrl + '. Continue?')) {
                e.preventDefault();
            }
        });
    });
</script>
"""
overall_time = 0.0

# Create a session and set headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
})

# List to store visited URLs
visited_urls = []

@app.route('/clone', methods=['GET', 'POST'])
def clone_site():
    global user_site
    if request.method == 'POST':
        site = request.form.get('site', '')
        if site.startswith('www'):
            site = 'https://' + site
        user_site = site.rstrip('/')
        return f"User site set to: {user_site}<br><br><a href='/'>Return"

    # Display visited URLs in the GET part
    visited_urls_str = '<br>'.join(visited_urls) if visited_urls else 'No visited URLs yet.'
    return f"""
Currently cloning: {user_site}

<form method='post'>
    <label for='site'>Enter Website URL:</label>
    <input type='text' id='site' name='site' value='https://'>
    <input type='submit' value='Clone'>
</form>
<br><br>
Visited URLs:
{overall_time}
<br><br>
{visited_urls_str}
"""

def fetch_and_modify_content(url):
    global user_site, visited_urls
    full_url = user_site + '/' + url
    visited_urls.append(full_url)
    # Record the start time for the operation
    start_time = time.time()
    try:
        response = session.get(full_url)
        content_type = response.headers['Content-Type']
        visited_urls.append(content_type)
        
        if not content_type.startswith('image'):
            html_content = response.content.replace(user_site.encode('utf-8'), server_url.encode('utf-8'))
            html_content = html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1)
            add_time_taken(start_time)
            visited_urls.append('Used Replace links@@@@@@@@@@@@@@@')
            return html_content, content_type
        add_time_taken(start_time)
        return response.content, content_type
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

def add_time_taken(start_time):
    global overall_time
    end_time = time.time()
    time_taken = end_time - start_time
    overall_time += time_taken


if __name__ == '__main__':
    app.run(debug=True)
