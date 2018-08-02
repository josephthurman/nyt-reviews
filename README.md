# NYTimes Food Reviews

The New York Times has a weekly restaurant review column, currently written by Pete Wells.  As part of the review process, the critic assigns a star rating to each restaurant, giving a maximum of four stars.  If the restaurant received no stars, then it is rated as "Satisfactory", "Fair", or "Poor".  

Although Wells is generally considered to be a good reviewer, readers sometimes complain that he uses the two-star rating too frequently.  In this project, we analyze Wells's reviews from the past 5 years to see if this is true.  

TBD: DESCRIBE THIS

## Obtaining the data
The New York Times offers an [API](https://developer.nytimes.com) that allows developers to access its archives.  This API returns article metadata, however, not the full text.  In order to obtain the data necessary for this project, we use this API to obtain a list of urls for all reviews written by Wells, then use the `BeautifulSoup` package to download each review and extract the relevant information from the html file.

### Getting the URLs
This is accomplished in `get_urls.py`. This script queries the NYT API for the urls for all reviews written by Pete Wells in the Food and Dining sections since January 1, 2013. Running this script requires an API key that is stored in a file `config.py`, not included in this repository for privacy's sake.

This query still returns some unwanted articles, including book reviews written by Wells, special content like slideshows and interactive media related to reviews, as well as reviews that don't actually include star ratings for an individual restaurant (e.g. best-of lists, reviews in the "Hungry City" column) and even a few articles that are mistakenly credited to Wells.  Some of these can be filtered out simply by inspecting the URL, which we do in this script.  The remainder cannot be distinguished without parsing the content of the page, and which is done later.

After this filtering, this script saves all of the URLS obtained to a text file called 'final_url_list.txt'.

### Getting the HTML for each Review
After the URLS, we download the HTML source for each page. This is done in `review_fetcher.py`, which fetches the source for each page and saves the result to a `/reviews/` folder for later analysis.  This also checks that the downloaded page is not an error page, and will re-download the page if an error page is encountered.

### Extracting the Data for each Review
We can then process the raw HTML for each review to extract the relevant data. This is done in `extract_info.py`.

In this script, each page is retrieved from the `/reviews/` and parsed using `BeautifulSoup`. From there, we define functions that extract the necessary information from the page. This is slightly difficult in that the template for reviews has changed repeatedly, and so different searches are necessary to find the relevant information in different templates. For each review, we extract
  * the full text of the review
  * the price range range of the expression measured from $ to $$$$
  * the number of recommended dishes at the restaurant
  * the final star rating, or category in case of 0 stars (e.g., 'Satisfactory')

Some pages still do not have star ratings that can be extracted.  These are saved by the script to the file `unprocessed_urls.txt`, where an inspection shows that none of these files include reviews that have a star rating, and so our script has successfully processed all of the reviews.  Some of these unprocessed reviews are regular reviews of restaurants outside of New York, and therefore do not receive a star rating.  We will revisit these reviews later to see what star rating for these reviews would be predicted by our model.

Finally, information extracted from each review is saved to a JSON file for the next part of the analysis.

## The Analysis

In this portion of the project, we attempt to build a model that can predict the star rating received by a restaurant using the other features of the review extracted above.

### Sentiment Analysis via Google


### Exploratory Analysis
