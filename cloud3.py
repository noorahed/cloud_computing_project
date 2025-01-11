import os
import datetime
import json
import tweepy
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
import firebase_admin
from firebase_admin import credentials, firestore

# Set local paths and credentials
json_path = r"C:\Users\FTS\Downloads\cloud\service_account.json"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAG3mxwEAAAAAQrqz9zbfGOP2HZYsAk9EGzl9X7U%3D7p4n9Q8BCgTHx5k2uyJxFLE5dfrs2qmg2ZXpSxEfIKOcel0Zir"  # Replace with your actual token

# Ensure the service account file exists
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Service account file not found at: {json_path}")

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(json_path)
    app = firebase_admin.initialize_app(cred)
else:
    app = firebase_admin.get_app()

# Initialize Firestore client
db = firestore.client()

def initialize_spark():
    """Initializes a Spark session."""
    return SparkSession.builder \
        .appName("Real-Time Sentiment Analysis") \
        .master("local[2]") \
        .getOrCreate()


def fetch_tweets(client, query, max_results=10):
    """Fetches recent tweets based on a query."""
    response = client.search_recent_tweets(query=f"{query} lang:en", 
                                           tweet_fields=["created_at", "author_id"], 
                                           max_results=max_results)
    return response.data


def save_tweets(response, filename="tweets_debug.json"):
    """Saves tweets to a JSON file for debugging."""
    with open(filename, "w") as f:
        tweets_data = [{"id": tweet.id, "text": tweet.text, "timestamp": str(tweet.created_at)} for tweet in response]
        json.dump(tweets_data, f, indent=4)


def preprocess_text(text):
    """Preprocesses text for sentiment analysis."""
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


def analyze_sentiment(text, model, tokenizer):
    """Analyzes sentiment of a text using RoBERTa model."""
    processed_text = preprocess_text(text)
    inputs = tokenizer(processed_text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    scores = outputs[0][0].detach().numpy()
    scores = softmax(scores)
    labels = ['Negative', 'Neutral', 'Positive']
    sentiment = labels[scores.argmax()]
    return sentiment


def save_to_firestore(df, db, collection_name="results"):
    """Saves the processed DataFrame to Firestore."""
    data_to_save = df.toJSON().collect()
    batch = db.batch()
    for json_data in data_to_save:
        tweet_dict = json.loads(json_data)
        doc_ref = db.collection(collection_name).document(str(tweet_dict['id']))
        batch.set(doc_ref, tweet_dict)
    batch.commit()

def retrieve_results(db, num=10):
    """Retrieves the last 'num' results from Firestore."""
    results_ref = db.collection("results").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(num)
    docs = results_ref.stream()
    for doc in docs:
        print(f"{doc.id} => {doc.to_dict()}")


def main():
    """Main function to orchestrate the sentiment analysis pipeline."""
    QUERY = "AI OR Data science"
    MAX_RESULTS = 10
    COLLECTION_NAME = "results"

    # Initialize Spark and Tweepy
    spark = initialize_spark()
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    # Fetch and save tweets
    tweets = fetch_tweets(client, QUERY, MAX_RESULTS)
    save_tweets(tweets)

    # Prepare data for Spark
    tweets_data = [{"id": tweet.id, "text": tweet.text, "timestamp": str(tweet.created_at)} for tweet in tweets]

    schema = StructType([
        StructField("id", StringType(), True),
        StructField("text", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])
    input_df = spark.createDataFrame(tweets_data, schema)

    # Load RoBERTa model and tokenizer
    task = 'sentiment'
    MODEL = f"cardiffnlp/twitter-roberta-base-{task}"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    # Register UDF for sentiment analysis
    sentiment_udf = udf(lambda text: analyze_sentiment(text, model, tokenizer), StringType())

    # Process data with sentiment analysis
    processed_df = input_df.withColumn("sentiment", sentiment_udf(col("text")))

    # Save to Firestore
    save_to_firestore(processed_df, db, COLLECTION_NAME)

    # Display processed data
    processed_df.show()

    # Cleanup
    spark.stop()


if __name__ == "__main__":
    main()
