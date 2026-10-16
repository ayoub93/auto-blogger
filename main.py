import os
import sys
import requests


def main():
    blog_id = os.getenv('BLOGGER_BLOG_ID', '').strip()
    client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN', '').strip()
    if not all([blog_id, client_id, client_secret, refresh_token]):
        print('Missing Blogger OAuth settings in GitHub Actions secrets.')
        sys.exit(1)
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }, timeout=30)
    response.raise_for_status()
    token = response.json()['access_token']
    response = requests.get('https://www.googleapis.com/blogger/v3/blogs/' + blog_id,
        headers={'Authorization': 'Bearer ' + token}, timeout=30)
    response.raise_for_status()
    print('Blogger API connection successful. No posts were published.')


if __name__ == '__main__':
    main()
