import requests
import json
from bs4 import BeautifulSoup

N = 10 # Number of times to try to fetch page

### NYT website has custom error page if it can't find the URL - this finds such pages so they can be re-downloaded
def find_server_error(bs):
    result = bs.find_all('meta', {'content': '500 - Server Error'})
    return(len(result) > 0)


with open('final_url_list.txt', 'r') as url_file:
    urls = json.load(url_file)

refetch = []

# First loop - download HTML for each url, check that it's valid, and save it if so
for counter, review_url in enumerate(urls):
    review = requests.get(review_url)
    parsed = BeautifulSoup(review.content, 'html.parser')
    if find_server_error(parsed):
        refetch.append(counter)
    else:
        with open('./reviews/review'+ str(counter) + '.html', 'w') as newfile:
            newfile.write(parsed.prettify())

# Retry on any pages that didn't download properly
missing = len(refetch)
attempts = 0
while (missing > 0) and (attempts <= 10):
    still_refetch = []
    for counter in refetch:
        print("Retrying to Fetch Review" + str(counter))
        review = requests.get(urls[counter])
        parsed = BeautifulSoup(review.content, 'html.parser')
        if find_server_error(parsed):
            still_refetch.append(counter)
        else:
            with open('./reviews/review' + str(counter) + '.html', 'w') as newfile:
                newfile.write(parsed.prettify())
    missing = len(still_refetch)
if missing > 0:
    print("Could not successfully access the following reviews:")
    for url in still_refetch:
        print(url)