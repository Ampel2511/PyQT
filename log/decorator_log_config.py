import sys
import logging

decorator_logger = logging.getLogger('decorator')

decorator_format = logging.Formatter('%(asctime)s %(message)s')

log_file = logging.FileHandler('decorator.log', encoding='utf8')
log_file.setFormatter(decorator_format)

client_stream_handler = logging.StreamHandler(sys.stderr)
client_stream_handler.setFormatter(decorator_format)
client_stream_handler.setLevel(logging.INFO)

decorator_logger.addHandler(log_file)
decorator_logger.addHandler(client_stream_handler)
decorator_logger.setLevel(logging.INFO)

if __name__ == '__main__':
    decorator_logger.critical('critical is worked')
    decorator_logger.error('error is worked')
    decorator_logger.info('info is worked')