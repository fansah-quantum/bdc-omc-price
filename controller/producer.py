from kafka import KafkaProducer 



class Producer:
    def __init__(self, bootstrap_servers, topic):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self.topic = topic


    def process_data(self, data):
        self.producer.send(self.topic, data.encode('utf-8'))


    def on_send_error(self, excp):
        print('I am an errback', excp)
        # handle exception
        pass

    def on_send_success(self, record_metadata):
        print(record_metadata.topic)
        print(record_metadata.partition)
        print(record_metadata.offset)
        pass

    


