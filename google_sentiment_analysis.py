# Standard imports
import json
import config
import copy

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()

with open('cleaned_review_data.json', 'r') as input:
    reviews = json.load(input)

# Pick an arbitrary review to check
test_text = reviews[115].get('review_text')

# Find sentiment in each text via Google
analyzed_reviews = []
for review in reviews:
    document = types.Document(content=review.get('review_text'), type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    google_score = sentiment.score
    google_mag = sentiment.magnitude
    new_review = copy.deepcopy(review)
    new_review['google_score'] = google_score
    new_review['google_mag'] = google_mag
    analyzed_reviews.append(new_review)

with open('analyzed_review_data.json', 'w') as outfile:
    json.dump(analyzed_reviews, outfile)

