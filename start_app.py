# this is point of entry for the app. It opens 6 different cmd prompts to execute commands for the app

import os
from configparser import ConfigParser
import time
import webbrowser

config = ConfigParser()

# read config file
config.read(".\kafka_spark_stream\configuration.conf")

#--------------------------------------------------------------------------
# 
# This is entry point for the app. It will open total 5 command prompts to exectue multiple commands # to start zkepper server, kafka, add topics to kafka, start tweet stream, start stream handler, 
# start node server and open brower to view live data. 
#
#       >>>>>>>>>>>>>> GAUTAM SAINI & SHILPI SIROHI <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#
#--------------------------------------------------------------------------

# cleanup temp directory zkserver
try:
    os.remove('./kafka_spark_stream/temp')
except OSError as e:
    pass

# start zkserver
os.system('start cmd /k "zkserver"')

#start kafka
time.sleep(5)
kafkaDir = config['Kafka_Data']['kafka_window_dir']
kakfa_cmds = "cd "+kafkaDir+"/bin/windows/ & kafka-server-start.bat "+kafkaDir+"/config/server.properties"
os.system('start cmd /k "'+kakfa_cmds+'"')

# create kafka topic for processing tweets
time.sleep(8)
kafkaDir = config['Kafka_Data']['kafka_window_dir']
kafka_topic_process_tweeets = config['App_Data']['tweet_topic_name']
kakfa_create_process_tweet_topic = "cd "+kafkaDir+"/bin/windows/ & kafka-topics.bat --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic "+kafka_topic_process_tweeets
os.system('start cmd /c "'+kakfa_create_process_tweet_topic+'"')

# create kafka topic for sentiment analysis tweets
kafkaDir = config['Kafka_Data']['kafka_window_dir']
kafka_topic_sentiments_tweeets = config['App_Data']['sentiment_topic_name']
kakfa_create_sentiment_tweet_topic = "cd "+kafkaDir+"/bin/windows/ & kafka-topics.bat --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic "+kafka_topic_sentiments_tweeets
os.system('start cmd /c "'+kakfa_create_sentiment_tweet_topic+'"')

#start streaming tweets
time.sleep(1)
streamer_cmds = "cd ./kafka_spark_stream/ & python stream_tweets.py"
os.system('start cmd /k "'+streamer_cmds+'"')

#start tweet handler
time.sleep(2)
handler_cmds = "cd ./kafka_spark_stream/ & python handler_tweets.py"
os.system('start cmd /k "'+handler_cmds+'"')

# #start nodejs server
time.sleep(2)
node_cmds = "cd ./node_server/ & node server.js"
os.system('start cmd /k "'+node_cmds+'"')

#open browser for testinig
time.sleep(1)
url = config['Node_data']['Host']+ ":" + config['Node_data']['Port'] +"/"
webbrowser.open(url)
print("end of code")