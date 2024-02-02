import os

server_url = os.getenv('url')

hearders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

js_code = f"""
<script>
    document.addEventListener('DOMContentLoaded', () => {{
        document.body.addEventListener('click', e => {{
            const targetUrl = e.target.getAttribute('href');
            const isExternalLink = targetUrl && targetUrl.startsWith('http') && !targetUrl.startsWith('{server_url}');
            
            if (isExternalLink && !window.confirm('You are leaving the proxy site and going to ' + targetUrl + '. Continue?')) {{
                e.preventDefault();
            }}
        }});
    }});
</script>
"""
