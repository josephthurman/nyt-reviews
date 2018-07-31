from bs4 import BeautifulSoup
import re
import json


# Some helper functions
def get_review(counter):
    with open('./reviews/review' + str(counter) + '.html', 'r') as file:
        parsed = BeautifulSoup(file, 'html.parser')
    return(parsed)


# Define functions for parsing

# Remove some misclassified content - Critic's Notebook and Hungry City columns
def is_misclassified(bs):
    if len(bs.find_all('meta', {'content': re.compile('Critic.*Notebook')})) > 0 :
        return(True)
    if re.search('<p.*?>\s*[Cc]ritic.*[Nn]otebook\s*</p>', str(bs)):
        return(True)
    if len(bs.find_all('meta', {'content': 'hungry-city'})) > 0:
        return(True)
    return(False)

# Extract the text of the review
def find_review(bs):
    tag_searches = [('p', re.compile('story-body-text story-content')),
                    ('p', re.compile('css-1i0edl6'))]

    for (tag, regex) in tag_searches:
        result = bs.find_all(tag, {'class': regex})
        if len(result) > 0:
            review_text = ''
            for p in result:
                review_text += p.get_text()
                review_text = re.sub(r'\s+', ' ', review_text)
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
            if stars in ['Satisfactory', 'Fair', 'Poor']:
                return(stars)
            else:
                return(str(len(stars)))

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
        return(str(len(just_stars)))
    # If all else fails, return 'NA' to show we couldn't find a rating
    return('NA')


# Extract the number of recommended dishes in the review
def find_rec_dishes(bs):
    tag_searches = [('div', 'class', re.compile('ReviewFooter-recommendedDishes')),
                    ('span', 'itemprop', re.compile('[Mm]enu'))]
    rec_dish_text = ''

    for (tag, property, regex) in tag_searches:
        result = bs.find_all(tag, {property: regex})
        if result:
            if len(result) > 1:
                rec_dish_text = result[1].get_text()
            else:
                rec_dish_text = result[0].get_text()
            break

    # Two reviews have the prices listed in a totally different format. We pick those up here
    if rec_dish_text == '':
        regex = re.compile(r'RECOMMENDED\s*</strong>(.*?)</p>', flags = re.DOTALL)
        rec_dish_text = re.search(regex, str(bs)).group(1)

    # Return the number of recommended dishes
    rec_dish_list = re.split('; |\. ', rec_dish_text)
    return(len(rec_dish_list))

# Convert numeric price to price category
# This is a best guess - they don't have a current key for this.
# But we're actually only doing this for 2 reviews anyway
def price_to_category(price):
    if price < 25:
        return(1)
    elif price < 50:
        return(2)
    elif price < 100:
        return(3)
    else:
        return(4)

# Extract the price rating in the review
def find_price(bs):
    tag_searches = [('dd', 'class', 'price'),
                    ('span', 'itemprop', re.compile('[Pp]rice[Rr]ange'))]
    price_text = ''
    for (tag, property, regex) in tag_searches:
        result = bs.find_all(tag, {property: regex})
        if len(result) > 0:
            price_text = result[0].get_text()
            break
    # Two reviews have the prices listed in a totally different format. We pick those up here
    if price_text == '':
        regex = re.compile(r'PRICES\s*</strong>(.*?)</p>', flags = re.DOTALL)
        price_text = re.search(regex, str(bs)).group(1)

    # Read price description and get the dollar sign rating
    dollar_regex = re.compile('(\$+)\s')
    dollarsigns = re.search(dollar_regex, price_text)
    if dollarsigns:
        return(len(dollarsigns.group(1)))
    else:
        # Extract actual price numbers - finds numbers preceded by $, or by hyphens for ranges,
        # e.g. return 5, 17 and 45 from somthing like "apps $5-17, entrees $45"
        price_regex = re.compile('(?<=[-\$])[0-9]+')
        list_of_prices = re.findall(price_regex, price_text)
        if list_of_prices:
            max_price = max(map(int,list_of_prices))
            return(price_to_category(max_price))
        else:
            # Error - couldn't find the price category.
            return(0)


########################################################
# Actual Processing begins here
with open('final_url_list.txt', 'r') as url_file:
    urls = json.load(url_file)

cleaned_reviews = []
unprocessed_URLS = []

for counter, review_url in enumerate(urls):
    # progress counter for debugging
    if counter % 10 == 0:
        print(counter)
    # Read review
    parsed = get_review(counter)
    if not is_misclassified(parsed):
        rating = find_stars(parsed)
        if rating != 'NA':
            restaurant_info = {'id': counter,
                               'review_url': review_url,
                               'rating': rating,
                               'review_text': find_review(parsed),
                               'price': find_price(parsed),
                               'rec_dishes' : find_rec_dishes(parsed)}
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