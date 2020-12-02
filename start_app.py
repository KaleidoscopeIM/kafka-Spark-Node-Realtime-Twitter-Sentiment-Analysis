import os
from configparser import ConfigParser
import time
import webbrowser

config = ConfigParser()
# read config file
config.read(".\kafka_spark_stream\configuration.conf")


# start zkserver
os.system('start cmd /k "zkserver"')

#start kafka
time.sleep(5)
kafkaDir = config['Kafka_installation']['kafka_window_dir']
kakfa_cmds = "cd "+kafkaDir+"/bin/windows/ & kafka-server-start.bat "+kafkaDir+"/config/server.properties"
os.system('start cmd /k "'+kakfa_cmds+'"')
#kafka-topics.bat --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic processSentiments
#start streaming tweets
time.sleep(8)
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
url = config['Node']['Host']+ ":" + config['Node']['Port'] +"/"
webbrowser.open(url)
print("end of code")