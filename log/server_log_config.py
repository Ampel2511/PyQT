import sys
import logging.handlers

server_logger = logging.getLogger('server')

server_format = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

log_file = logging.handlers.TimedRotatingFileHandler('server.log', interval=1, when='D', encoding='utf8')
log_file.setFormatter(server_format)

server_stream_handler = logging.StreamHandler(sys.stderr)
server_stream_handler.setFormatter(server_format)
server_stream_handler.setLevel(logging.INFO)

server_logger.addHandler(log_file)
server_logger.addHandler(server_stream_handler)
server_logger.setLevel(logging.INFO)

if __name__ == '__main__':
    server_logger.critical('critical is worked')
    server_logger.error('error is worked')
    server_logger.info('info is worked')
