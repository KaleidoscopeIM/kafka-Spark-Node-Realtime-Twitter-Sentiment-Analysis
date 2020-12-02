from os import environ
from kafka import KafkaProducer
from configparser import ConfigParser
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row, SQLContext
import json
import sys
from textblob import TextBlob


def sum_all_tags(new_counts, total_saved):
    if total_saved is None:
        return sum(new_counts)
    return sum(new_counts) + total_saved

def getSparkSessionInstance(spark_context):
    if ('sparkSessionSingletonInstance' not in globals()):
        globals()['sparkSessionSingletonInstance'] = SQLContext(spark_context)
    return globals()['sparkSessionSingletonInstance']


def getKafkaInstance():
    # Creating the gloabal instance of Kafka Producer only once
    if ('kafkaSingletonInstance' not in globals()):
        globals()['kafkaSingletonInstance'] = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    return globals()['kafkaSingletonInstance']

def send_to_kafka(hashtagCountsDataFrame, topic):

    data = {}
    for tags, frequency in hashtagCountsDataFrame.collect():
        data[tags] = frequency
    # producer will produce analysed tweets
    producer = getKafkaInstance()
    # send analysis to kafka topic
    producer.send(globals()[topic], value=data)
    
def process_hashtags(time, rdd):
    try:
        print("---------Processing tags data--------".format(time))
        sql_instance = getSparkSessionInstance(rdd.context)
        rowRdd = rdd.map(lambda tag: Row(hashtagwords=tag[0], frequency=tag[1]))
        # create a local table for storing streaming data
        sql_instance.createDataFrame(rowRdd).createOrReplaceTempView("wordstable")
        
        # fetch top 5 words hashtags
        df = sql_instance.sql(
            "select hashtagwords, frequency from wordstable order by frequency desc limit 5")
        df.show()
        
        send_to_kafka(df,'tweet_topic_name')
    except:
        e = sys.exc_info()[0]
        print(e)


def process_sentiment(time, rdd):
    try:
        print("---------Processing sentiment data--------".format(time))
        sql_instance = getSparkSessionInstance(rdd.context)
        rowRdd = rdd.map(lambda tag: Row(tweet=tag[0], frequency=tag[1]))
        sql_instance.createDataFrame(rowRdd).createOrReplaceTempView("sentiments_table")
        #fetch all tweets for sentiment analysis
        df = sql_instance.sql(
            "select tweet, frequency from sentiments_table order by frequency")
        df.show()
        send_to_kafka(df,'sentiment_topic_name')
    except:
        e = sys.exc_info()[0]
        print(e)
    

if __name__ == "__main__":

    config = ConfigParser()

    #setup confifuration for the app
    config.read(".\configuration.conf")
    globals()['tweet_topic_name'] = config['App_Data']['tweet_topic_name']
    globals()['sentiment_topic_name'] = config['App_Data']['sentiment_topic_name']
    environ['PYSPARK_SUBMIT_ARGS'] = config['App_Data']['pyspark_environ']
    sparkConf = SparkConf(config['Spark_data']['config_name'])

    # setting number of receivers = 2
    # 1 = kafka, 2= rdd processing
    sparkConf.setMaster("local[2]")
    sc = SparkContext(conf=sparkConf)
    sc.setLogLevel("ERROR")
    sqlContxt = SQLContext(sc)
    ssc = StreamingContext(sc, 30)

    # Setup temp folder rdd data storage and recovery by checkpint
    ssc.checkpoint("temp")
    
    # setup kafka
    kafkaParam = {
        "zookeeper.connect": config['Kafka_Data']['zookeeper.connect'],
        "group.id": config['Kafka_Data']['group.id'],
        "zookeeper.connection.timeout.ms": str(15000),
        "bootstrap.servers": config['Kafka_Data']['bootstrap.servers']
    }

    # Creating Dstream from Kafka input
    tweets = KafkaUtils.createDirectStream(
        ssc, [config['App_Data']['app_name']], kafkaParams=kafkaParam, valueDecoder=lambda x: json.loads(x.decode('utf-8')))
    
    # Get tweet sterem to perform sentiment analysis - Shilpi
    tweet_stream = tweets.map(lambda tweet_data: tweet_data[1]["text"])
    tweetSentiment = tweet_stream.map(lambda t: TextBlob(t).sentiment.polarity)
    setVar= tweetSentiment.map(lambda x: 'positive' if x>0.5 else ('neutral' if x==0.5 else 'negative'))
    sentmentCount=setVar.countByValue()
    sentmentCount.pprint()
    sentmentCount.foreachRDD(process_sentiment)

    # create another strem for tag analysis
    words_list = tweets.map(lambda v: v[1]["text"]).flatMap(lambda t: t.split(" "))
    words_list.count().pprint()
    hashtag_data = words_list.filter(lambda tag: len(tag)>2 and '#' == tag[0]).countByValue().updateStateByKey(sum_all_tags)
    hashtag_data.pprint()
    hashtag_data.foreachRDD(process_hashtags)

    # Start Streaming Context
    ssc.start()
    ssc.awaitTermination()
