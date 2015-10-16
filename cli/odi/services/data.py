import requests
import unicodecsv as csv


def load(url):
    """Load json results from url.
    """
    req = requests.get(url)
    json = req.json()
    results = json['results']
    return results


def save(items, fieldnames, path):
    """Save list of dicts to csv with fieldnames.
    """
    with open(path, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in items:
            writer.writerow(item)
