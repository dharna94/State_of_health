from celery import group
from flask import Blueprint, jsonify, url_for
import json
from flask import request
from celery import Celery
from tqdm import tqdm
from SOH_API.celery_worker import group_vins


# celery_app = Celery('simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Creating Blueprint Object
SOH_MAIN_ = Blueprint('SOH Main File', __name__)

@SOH_MAIN_.route('/index')
def index():
    name = "SOH Rest Api"
    print(name)
    return name

@SOH_MAIN_.route('/get_soh_details', methods=['POST'])
def get_SOH():
    total = 10
    parameters = json.loads(request.data)
    vin_list = parameters['vins']
    print(vin_list)
    # queue name in task folder.function name
    # for vin in vin_list:
    #     r = celery_app.send_task('celery_worker.get_data', kwargs={'vin': vin})
    #     print(r)
    # return r.id
    delayed_results = group_vins.delay(vin_list)
    # results = []
    print(delayed_results)
    # for result in tqdm(delayed_results.children, total=total):
    #     results.append(result.get())
    response = {
        "output":{
            "task":delayed_results.id,
            "task_url":url_for(
                "SOH Main File.check_task",task_id=delayed_results.id, _external=True
            )
        }
    }
    return jsonify(response), 202, response


@SOH_MAIN_.route('/status/<task_id>')
def check_task(task_id):
    task = group_vins.AsyncResult(task_id)
    response = {
        'state': task.state
    }
    # if task.state == 'PENDING':
    #     response = {
    #         'state': task.state,
    #         'current': 0,
    #         'total': 1,
    #         'status': 'Pending...'
    #     }
    # elif task.state != 'FAILURE':
    #     response = {
    #         'state': task.state,
    #         'current': task.info.get('current', 0),
    #         'total': task.info.get('total', 1),
    #         'status': task.info.get('status', '')
    #     }
    #     if 'result' in task.info:
    #         response['result'] = task.info['result']
    # else:
    #     # something went wrong in the background job
    #     response = {
    #         'state': task.state,
    #         'current': 1,
    #         'total': 1,
    #         'status': str(task.info),  # this is the exception raised
    #     }
    return jsonify(response)