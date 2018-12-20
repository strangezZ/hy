import logging
import configparser
import os
import sys
import asyncio
from threading import Thread
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from handlers.work_order_handler import init_work_order_handler, find_and_send_task, delete_finish_task


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def set_log():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_name = 'hyjt_erp.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, 'w+')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def main():

    set_log()
    logging.info("program start")
    conf = configparser.ConfigParser()
    conf.read(os.path.dirname(os.path.realpath(sys.argv[0])) + '/config.cfg')

    logging.info("configure start")
    sqlserver_host = conf.get("sqlserver","host")
    dbname = conf.get("sqlserver","dbname")
    if init_work_order_handler(conf) is False:
        return
    logging.info("configure end")

    logging.info("sqlserver connecting start")
    sqlserver_engine = sqlalchemy.create_engine(sqlserver_host + dbname)
    Session = sessionmaker(bind=sqlserver_engine)
    logging.info("sqlserver connecting end")

    new_loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(new_loop,))
    t.start()
    logging.info("start request_sending_task")
    asyncio.run_coroutine_threadsafe(find_and_send_task(Session, new_loop), new_loop)
    logging.info("start delete_finish_task")
    asyncio.run_coroutine_threadsafe(delete_finish_task(Session, new_loop), new_loop)
    t.join()
    logging.info("program exit")


if __name__ == '__main__':
    main()
