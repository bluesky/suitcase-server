from functools import partial
import enum
import importlib
import time
import uuid

from concurrent.futures import ProcessPoolExecutor
from suitcase.utils import MemoryBuffersManager

job_cache = {}
executor = ProcessPoolExecutor()


class JobStatus(enum.Enum):
    created = enum.auto()
    ready = enum.auto()


def serialize(suitcase, uid, kwargs):
    module = importlib.import_module(f'suitcase.{suitcase}')
    serializer_class = getattr(module, 'Serializer')
    manager = MemoryBuffersManager()
    # documents = catalog[uid].read_canonical()
    # with serializer_class(manager, **kwargs) as serializer:
    #     for item in documents:
    #         serializer(*item)
    return manager.artifacts


def submit_job(suitcase, uid, kwargs):
    job_id = str(uuid.uuid4())
    job_info = {'creation_time': time.time(),
                'status': JobStatus.created}
    job_cache[job_id] = job_info
    future = executor.submit(serialize, suitcase, uid, kwargs)
    future.add_done_callback(partial(cache_result, job_info=job_info))
    return job_id


def cache_result(future, job_info):
    artifacts = future.result()
    job_info['artifacts'] = artifacts
    job_info['ready_time'] = time.time()
    job_info['status'] = JobStatus.ready


def get_job(job_id):
    return job_cache[job_id]

    
class JobGarbageCollected(Exception):
    ...
