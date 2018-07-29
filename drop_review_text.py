import json

with open('analyzed_review_data.json', 'r') as input:
    reviews = json.load(input)

for i in range(len(reviews)):
    record = reviews[i]
    record.pop('review_text')

with open('sentiments.json', 'w') as output:
    json.dump(reviews, output)