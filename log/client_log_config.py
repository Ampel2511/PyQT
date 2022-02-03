import sys
import logging

client_logger = logging.getLogger('client')

client_format = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

log_file = logging.FileHandler('client.log', encoding='utf8')
log_file.setFormatter(client_format)

client_stream_handler = logging.StreamHandler(sys.stderr)
client_stream_handler.setFormatter(client_format)
client_stream_handler.setLevel(logging.INFO)

client_logger.addHandler(log_file)
client_logger.addHandler(client_stream_handler)
client_logger.setLevel(logging.INFO)

if __name__ == '__main__':
    client_logger.critical('critical is worked')
    client_logger.error('error is worked')
    client_logger.info('info is worked')
