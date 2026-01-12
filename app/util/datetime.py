from datetime import datetime
import pytz
from app.core.config import settings

timezone_app = pytz.FixedOffset(settings.TIME_ZONE * 60)

def get_current_time():
    return datetime.now(timezone_app).replace(tzinfo=None)