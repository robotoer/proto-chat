import logging

def get(name):
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)

  console_log = logging.StreamHandler()
  console_log.setLevel(logging.DEBUG)

  file_log = logging.FileHandler('{}.log'.format(name))
  file_log.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  file_log.setFormatter(formatter)

  logger.addHandler(console_log)
  logger.addHandler(file_log)

  return logger
