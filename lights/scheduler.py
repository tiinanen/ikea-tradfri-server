from apscheduler.schedulers.background import BackgroundScheduler as SchedulerType
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class LightScheduler:
    def __init__(self, db_conn_str=None):
        if db_conn_str is None:
            db_conn_str = "sqlite:///scheduler_db.sqlite"
        self._jobstores = {'default' : SQLAlchemyJobStore(db_conn_str)}
        self.scheduler = SchedulerType(jobstores=self._jobstores)
        self.scheduler.start()

    def add_job(self, fn, fn_args=None, fn_kwargs=None, **kwargs):
        return self.scheduler.add_job(fn, args=fn_args, kwargs=fn_kwargs, coalesce=True, replace_existing=True, **kwargs)

    def get_jobs(self):
        return self.scheduler.get_jobs()

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

