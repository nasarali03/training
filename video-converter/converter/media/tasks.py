# media/tasks.py
from celery import shared_task
import time
from .utils import convert
@shared_task
def test_celery_task(x, y):
    print(f"Task started with values: {x}, {y}")
    time.sleep(5)  # simulate heavy processing
    result = x + y
    print(f"Task completed: {result}")
    return result

# @shared_task
# def test_celery_task(a,b):
#     i=0
#     while i < 5:
#         time.sleep(1)
#         print("Processing....")
#         i+=1
#     return a+b

@shared_task
def process_video(input_path,output_path):
    return convert(input_path,output_path)