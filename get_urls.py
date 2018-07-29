import config
import requests
import json
import time
import re


query_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json' + \
              '?api_key=' + config.NYT_API_KEY  + '&begin_date=20130101' + '&fl=web_url' + \
              '&fq=byline:("Pete Wells")ANDtype_of_material:("Review")ANDnews_desk:("Dining","Food")'

# There are 336 records returned by this query, which can be obtained from the metadata returned by the first request
# Each query returns 10 records at a time, controlled by the "page" variable - page 0 gives records 1-10,
# page 1 gives 11-20, etc. Thus we loop to page 33 to see all records
# We could compute 33 instead of hard-coding it in, but we're only going to run the script once
returned_url_list = []
for page in range(34):
    results = requests.get(query_url+'&page='+str(page)).json()
    response = results.get('response')
    if response is not None:
        current_article_list = response.get('docs')
        for article in current_article_list:
            url = article.get('web_url')
            returned_url_list.append(url)
    time.sleep(2) #Can't make too many requests per second or the API gets mad

print(len(returned_url_list))

# After inspection, this still contains some articles we don't want - book reviews written by Pete Wells,
# some misclassified recipes, special content related to a review that's not actually the review itself, etc.
# We can find some of these by inspecting the url, and we remove those now.
bad_words = ["(blog)", "(interactive)", "(wine-school)", "(insider)", "(hungry-city)", "(best)",
             "(/books/)", "(slideshow)", "(obituaries)", "(recipes)", "(reader-center)", "(technology)"]

final_url_list = []
for url in returned_url_list:
    if not re.search("|".join(bad_words), url):
        final_url_list.append(url)
print(len(final_url_list))

with open('final_url_list.txt', 'w') as outfile:
    json.dump(final_url_list, outfile)

