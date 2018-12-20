import logging
import json
import asyncio
import time

import requests
from sqlalchemy.orm import scoped_session
from entities.task import Task
from networking.http_client import get_http_request_data, get_http_request, async_http_client

work_order_sending_url = ''
finish_task_data = []
last_updata_time = ''

def joint_request_data(task):
    task_dict = {}
    task_dict['task_type'] = 'hy'
    task_dict['task_serial'] = task.code
    task_dict['task_date'] = task.introducerDate
    task_dict['product_code'] = task.materalcode
    task_dict['product_name'] = task.materalcode
    task_dict['plan_num'] = task.quantity
    task_dict['plan_serial'] = task.refercode
    task_dict['plan_start'] = task.introducerDate
    task_dict['plan_end'] = task.finishdate
    task_dict['work_center'] = task.defineStr2
    task_dict['modifydate'] = task.modifydate
    return task_dict

def init_work_order_handler(config):
    global work_order_sending_url
    mes_url = config.get("mes", "mes_url")
    task_api = config.get("mes", "task_api")
    if mes_url is None or task_api is None:
        logging.info("Close find_and_send_task because config.cfg's "
                     "mes_url or task_api is None")
        return False
    work_order_sending_url = mes_url + task_api
    return True

async def find_and_send_task(session_factory, event_loop):

    try:
        global finish_task_data
        global last_updata_time
        while True:
            session = scoped_session(session_factory)
            tasks = session.query(Task).filter(Task.Auditing != "N",Task.modifydate > last_updata_time).all()
            request_data = {"tasks": []}
            for task in tasks:
                if task.Auditing == 'Y' and task.defineStr1 != 8:
                    task_dict = joint_request_data(task)
                    request_data["tasks"].append(task_dict)
                elif task.defineStr1 == 8:
                    finish_task_data.append(task)
            try:
                failed_task_tag_list = await request_sending_task(request_data)
                if len(failed_task_tag_list) == 0:
                    logging.info('send successfully')
                else:
                    failed_task_tags = str(failed_task_tag_list)
                    logging.info("Error:failed_task_tags" + failed_task_tags + "sending failure")
            except Exception as e:
                logging.info(e)
            await asyncio.sleep(8)
    except Exception as e:
        logging.info(e)
        logging.info("Restart find_and_send_task")
        asyncio.run_coroutine_threadsafe(find_and_send_task(session_factory, event_loop), event_loop)

async def delete_finish_task(session_factory, event_loop):
    try:
        while True:
            global finish_task_data
            if len(finish_task_data) > 0:
                request_data = {"tasks": []}
                for finish_task in finish_task_data:
                    task_dict = joint_request_data(finish_task)
                    request_data["tasks"].append(task_dict)
                    encode_request_data = get_http_request_data(request_data)
                    response = requests.post(work_order_sending_url, data=encode_request_data)
                    data = response.json()
                    if data['errno'] != 0:
                        logging.info(data['errmsg'])
                    else:
                        logging.info('delete successfully')
            else:
                logging.info('No finish task')
            await asyncio.sleep(8)
    except Exception as e:
        logging.info(e)
        logging.info("Restart delete_finish_task")
        asyncio.run_coroutine_threadsafe(delete_finish_task(session_factory, event_loop), event_loop)

async def request_sending_task(request_data):

    if len(request_data["tasks"]) > 0:
        encode_request_data = get_http_request_data(request_data)
        try:
            response = requests.post(work_order_sending_url, data=encode_request_data)
            data = response.json()
            if data['errno'] != 0:
                logging.info(data['errmsg'])
                return None
            else:
                logging.info("Request send_task cause error : " + data['errmsg'])
                failed_tasks = data['result']['failed_tasks']
                failed_task_tags = []
                for failed_task in failed_tasks:
                    failed_task_tags.append(failed_task['task_type'] + "#" + failed_task['task_serial'])
                return failed_task_tags

        except Exception:
            raise










