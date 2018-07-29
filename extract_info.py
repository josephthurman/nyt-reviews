from bs4 import BeautifulSoup
import re
import json

# Define functions for parsing

# Remove some misclassified content - Critic's Notebook and Hungry City columns
def is_misclassified(bs):
    nb_search = re.compile('Critic.*Notebook')
    if len(bs.find_all('meta', {'content': nb_search})) > 0 :
        return(True)
    if re.search('<p.*?>\s*[Cc]ritic.*[Nn]otebook\s*</p>', str(bs)):
        return(True)
    if len(bs.find_all('meta', {'content': 'hungry-city'})) > 0:
        return(True)
    return(False)

# Extract the text of the review
def find_review(bs):
    tag_searches = [('p', re.compile('story-body-text story-content')),
                    ('p', re.compile('css-1i0edl6*'))]

    for (tag, regex) in tag_searches:
        result = bs.find_all(tag, {'class': regex})
        if len(result) > 0:
            review_text = ''
            for p in result:
                review_text += p.get_text() + '\n'
            return(review_text)
    # Return EMPTY if review text cannot be found
    return("EMPTY")

# Extract the rating from the review
def find_stars(bs):
    # Newer reviews have the rating set off from the story in special html tag.  Find those first
    tag_searches = [('span', re.compile('ReviewFooter-stars')),
                ('div', re.compile('ReviewFooter-rating')),
                ('li', re.compile('critic-star-rating')),
                ('li', re.compile('critic-word-rating'))]
    stars = "NA"
    for (tag, regex) in tag_searches:
        result = bs.find_all(tag, {'class': regex})
        if len(result) > 0:
            text = result[0].get_text()
            stars = re.sub(r'\s+', ' ', text).strip()
            return(stars)

    # Older stories have the rating just sitting in a plain paragraph. We can also find those
    if re.search('<p.*?>\s*[Ss]atisfactory\s*</p>', str(bs)):
        return('Satisfactory')
    if re.search('<p.*?>\s*[Ff]air\s*</p>', str(bs)):
        return('Fair')
    if re.search('<p.*?>\s*[Pp]oor\s*</p>', str(bs)):
        return('Poor')
    direct_search = re.search('<p.*?>\s*★+\s*</p>', str(bs))
    if direct_search:
        just_stars = re.search('★+', direct_search.group()).group()
        return('★'* len(just_stars))
    # If all else fails, return 'NA' to show we couldn't find a rating
    return('NA')


# Processing begins here
with open('final_url_list.txt', 'r') as url_file:
    urls = json.load(url_file)

cleaned_reviews = []
unprocessed_URLS = []
for counter, review_url in enumerate(urls):
    # progress counter for debugging
    if counter % 10 == 0:
        print(counter)
    # Read review
    with open('./reviews/review'+ str(counter) + '.html', 'r') as file:
        parsed = BeautifulSoup(file, 'html.parser')
        if not is_misclassified(parsed):
            rating = find_stars(parsed)
            if rating != 'NA':
                restaurant_info = { 'id' : counter,
                                    'review_url' : review_url,
                                    'rating' : rating,
                                    'review_text': find_review(parsed)}
                cleaned_reviews.append(restaurant_info)
            else:
                unprocessed_URLS.append(review_url)

# Record reviews for which a rating couldn't be found, but which is not in one of the misclassified categories
# (e.g., Hungry City or Critic's Notebook)
# This list ends up being short enough to inspect by hand and see that each is not a restaurant review with the star
# system - some are reviews of out-of-town restaurants, and some are special non-review articles that have still
# managed to slip by
with open('unprocessed_URLs.txt', 'w') as outfile:
    json.dump(unprocessed_URLS, outfile)

# Save cleaned reviews for further analysis
with open('cleaned_review_data.json', 'w') as outfile:
    json.dump(cleaned_reviews, outfile)
