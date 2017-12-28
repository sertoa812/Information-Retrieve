from ESClass import ESClass
import pika
import os
News_path = os.path.join(os.path.abspath('..'),'News')
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1', port=5672))  # 定义连接池
channel = connection.channel()

channel.queue_declare(queue='news')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    print()
    es = ESClass('http://localhost:9200/')
    if es.check_index_if_exists():
        es.insert_crawled_data(os.path.join(News_path+'/'+body.decode('utf-8')))
    ch.basic_ack(delivery_tag=method.delivery_tag)  # 主要使用此代码

channel.basic_consume(callback,
                      queue='news',
                      no_ack=False)
channel.start_consuming()
