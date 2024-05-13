import requests
from bs4 import BeautifulSoup
import csv

def fetch_writeup_details(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the challenge title
    page_header = soup.find('div', class_='page-header')
    title = page_header.find('h2').text.strip() if page_header else 'No Title'

    # Check for the presence of the description div
    description = soup.find('div', id='id_description')
    if not description or not description.text.strip():
        return None  # Ignore entries without a description

    description_content = description.text.strip()

    # Extract tags from the specific <p> tag within <div class="span7">
    tags_container = soup.find('div', class_='span7')
    if tags_container:
        p_tag = tags_container.find('p')  # Find the first <p> tag within the div
        if p_tag:
            tags = [tag.text.strip() for tag in p_tag.find_all('span', class_='label label-info')]
        else:
            tags = []
    else:
        tags = []

    return {'title': title, 'url': url, 'tags': ', '.join(tags), 'description': description_content}

def scrape_ctf_writeups():
    base_url = 'https://ctftime.org/writeup/'
    writeups = []

    for i in range(1, 100000):  # Adjust the range as needed
        url = f'{base_url}{i}'
        details = fetch_writeup_details(url)
        if details:
            writeups.append(details)
            print(f'Scraped: {details["title"]}')

    # Save to CSV
    with open('ctf_writeups.csv', 'w', newline='') as file:
        fieldnames = ['title', 'url', 'tags', 'description']
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)  # Ensure all fields are quoted
        writer.writeheader()
        for writeup in writeups:
            writer.writerow(writeup)

if __name__ == '__main__':
    scrape_ctf_writeups()
