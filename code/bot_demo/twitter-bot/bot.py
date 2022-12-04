# MISOGYNY DETECTION TWITTER BOT

# Import packages
import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

##################################################################################

# TRAIN NAIVE BAYES MODEL
#LOAD FILE
df=pd.read_csv('./../../cleaned_tweets.csv')  # 'cleaned_tweets.csv'

print("Cleaning data...")
#CONVERT FROM STRING LABELS TO INTEGERS 
labels=[]; #y1=[]; y2=[]
y1=[]
for label in df["label"]:
    if label not in labels:
        labels.append(label)
    for i in range(0,len(labels)):
        if(label==labels[i]):
            y1.append(i)
y1=np.array(y1)

# CONVERT DF TO LIST OF STRINGS 
corpus=df["tweets"].to_list()

# INITIALIZE COUNT VECTORIZER
# minDF = 0.01 means "ignore terms that appear in less than 1% of the documents". 
# minDF = 5 means "ignore terms that appear in less than 5 documents".
vectorizer=CountVectorizer(min_df=0.001)   

# RUN COUNT VECTORIZER ON OUR COURPUS 
Xs  =  vectorizer.fit_transform(corpus)   
X=np.array(Xs.todense())

#CONVERT TO ONE-HOT VECTORS
X = (X != 0).astype(int)

test_ratio=0.2

# SPLIT ARRAYS OR MATRICES INTO RANDOM TRAIN AND TEST SUBSETS.
x_train, x_test, y_train, y_test = train_test_split(X, y1, test_size=test_ratio, random_state=0)
y_train=y_train.flatten()
y_test=y_test.flatten()

print("Training model...")
# INITIALIZE MODEL 
model = MultinomialNB()

# TRAIN MODEL 
model.fit(x_train,y_train)

##################################################################################

# CREATE BOT
from newspaper import Article
import tweepy
import config

# Get authentication keys from config
auth = tweepy.OAuth1UserHandler(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)

# Save authentication
api = tweepy.API(auth)

# Define tweepy streaming client
# Code reference: https://stackoverflow.com/questions/65416806/how-do-i-get-the-tweet-someone-is-mentioning-my-bots-username-in-reply-to-with
class MyStreamListener(tweepy.StreamingClient):
   def on_tweet(self, tweet):
      BOT_ID = '1596200849130283008'

      # Exit the function if responding to itself
      if str(tweet.author_id) == BOT_ID:
         return

      # SAVE DATA FROM TWEET
      # Save tweet sender's username
      sender_user = api.get_user(user_id=tweet.author_id)
      sender_username = sender_user.screen_name

      # Save tweet id
      sender_tweet_id = tweet.id

      # Save first url in tweet
      try:
         article_url = tweet.entities['urls'][0]['expanded_url']
      except KeyError:
         # If no URL is present in the tweet, notify the user.
         print("No URL in tweet")
         key_error_message = "I could not detect a URL in this tweet. Please @ me again with a URL to an article."
         self.response(key_error_message, sender_username, sender_tweet_id)
         return

      # Print data
      print("URL:", article_url)
      print("Username:", sender_username)
      print("Text:", tweet.text)

      # ANALYZE ARTICLE
      message = self.article_analysis(article_url)

      # RESPOND TO TWEET
      self.response(message, sender_username, sender_tweet_id)

   def response(self, message, user_to, tweet_reply_id):
      reply_tweet = "@" + str(user_to) + " " + message
      api.update_status(reply_tweet, in_reply_to_status_id = tweet_reply_id)
      print("Response tweet:", reply_tweet)

   def article_analysis(self, url):
      # Scrape article from web
      X_article = Article(url)
      X_article.download()
      X_article.parse()
      X_article.nlp()

      # Save text
      article_text = [X_article.text]

      # Run trained vectorizer on the article text
      art_X_sparse = vectorizer.transform(article_text)
      art_X = np.array(art_X_sparse.todense())

      # Convert to one-hot vectors
      #CONVERT TO ONE-HOT VECTORS
      art_X = (art_X != 0).astype(int)

      result = model.predict(art_X)[0]

      if result == 0:
         result_string = "does not"
      else:
         result_string = "does"

      report = "The linked article ({}) {} contain misogynistic sentiments.".format(
         X_article.title,
         result_string
      )

      return report

   def on_error(self, status_code):
      if status_code == 420:
         print("rate limit reached") 
         return False

##################################################################################

# RUN BOT
# Initialize stream
stream = MyStreamListener(bearer_token=config.bearer_token)

# Add rule to stream--listen for mentions
stream.add_rules(tweepy.StreamRule("@miso_detection"))

# Begin stream
print("Listening...")
stream.filter(tweet_fields=['entities','author_id'])
