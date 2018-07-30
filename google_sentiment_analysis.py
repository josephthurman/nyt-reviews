# Standard imports
import json
import config
import copy
import re

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()

with open('cleaned_review_data.json', 'r') as input:
    reviews = json.load(input)


# Find sentiment in each text via Google
analyzed_reviews = []
for review in reviews:
    text1 = review.get('review_text')
    text2 = re.sub(r'\s+', ' ', text1)

    # With extraneous whitespace
    document = types.Document(content=text1, type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    google_score1 = sentiment.score
    google_mag1 = sentiment.magnitude

    # Without - we want this one, seems to give a little more variation
    document = types.Document(content=text2, type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    google_score2 = sentiment.score
    google_mag2 = sentiment.magnitude

    # Save
    new_review = copy.deepcopy(review)
    new_review['google_score1'] = google_score1
    new_review['google_mag1'] = google_mag1
    new_review['google_score2'] = google_score2
    new_review['google_mag2'] = google_mag2
    analyzed_reviews.append(new_review)

with open('analyzed_review_data.json', 'w') as outfile:
    json.dump(analyzed_reviews, outfile)

