# Standard imports
import json

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()

with open('./data/cleaned_reviews.json', 'r') as input:
    reviews = json.load(input)

# Find sentiment in each text via Google
for counter in range(len(reviews)):
    review = reviews[counter]
    text = review.get('review_text')

    # Analysis via Google
    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    google_score = sentiment.score
    google_mag = sentiment.magnitude

    # Save
    review['google_score'] = google_score
    review['google_mag'] = google_mag

with open('./data/google_sentiments.json', 'w') as outfile:
    json.dump(reviews, outfile)
