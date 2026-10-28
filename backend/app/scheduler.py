from apscheduler.schedulers.blocking import BlockingScheduler
from app.db import SessionLocal
from app.repository import Repository
from app.notification_service import NotificationService

def run_reminders():
    with SessionLocal.begin() as db: NotificationService(Repository(db)).run()

if __name__=='__main__':
    scheduler=BlockingScheduler(timezone='Asia/Ho_Chi_Minh')
    from app.config import settings
    if settings.knowledge_rag_enabled and (settings.gemini_api_key or settings.llm_api_key):
        from app.knowledge.service import tick
        scheduler.add_job(tick,'interval',minutes=1,id='knowledge-ingestion',max_instances=1,coalesce=True)
    scheduler.add_job(run_reminders,'cron',hour=7,minute=0,id='daily-reminders',max_instances=1,coalesce=True,misfire_grace_time=3600)
    run_reminders()
    scheduler.start()
