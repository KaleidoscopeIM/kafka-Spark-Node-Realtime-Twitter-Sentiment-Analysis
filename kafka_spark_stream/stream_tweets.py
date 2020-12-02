import tweepy
import json
import sys
from kafka import KafkaProducer
from configparser import ConfigParser

class Listener(tweepy.StreamListener):
    processed_tweet_count = 0
    producer = None
    app_name = None
    
    def __init__(self, kafka_producer):
        self.app_name = config['App_Data']['app_name']
        self.producer = kafka_producer        
        self.count = 0

    def on_data(self, json_data):
        data = json.loads(json_data)
        if '#' in data["text"]:       
            self.producer.send(self.app_name, value={"text": data["text"]})
            print(data["text"])
            self.processed_tweet_count += 1    
            print("-------------------------------------- ", end="Tweets processed = " +str(self.processed_tweet_count) +"\n")     
                 

    def on_error(self, status_code):
        print("Error in streaming data")
        print(status_code)


class StreamTweets():

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth, listener)

    def start(self):
        language = config['Tweet_Params']['language'].split(' ')
        track_keywords = config['Tweet_Params']['keywords'].split(' ')
        location = [float(aLoc) for aLoc in config['Tweet_Params']['location'].split(',')]  
        self.stream.filter(languages=language,track=track_keywords, locations=location)

if __name__ == "__main__":

    config = ConfigParser()
    config.read(".\configuration.conf")

    bootstap_server = config['Kafka_Data']['bootstrap.servers']
    producer = KafkaProducer(bootstrap_servers=[bootstap_server],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    
    # using tweepy to conenct to twitter .. standard api of tweepy
    consumer_key = config['API_details']['consumer_key']
    consumer_secret = config['API_details']['consumer_secret']
    access_token = config['API_details']['access_token']
    access_secret = config['API_details']['access_secret']    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    
    listener = Listener(producer)
    stream = StreamTweets(auth, listener)

    # Converting string to float to get cordinates  
    stream.start()
