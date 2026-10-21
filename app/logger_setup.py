import logging
import re

class PIIRedactionFilter(logging.Filter):
    def filter(self, record):
        # إخفاء أي رقم تليفون (أرقام تبدأ بـ + أو أرقام متتالية طويلة)
        record.msg = re.sub(r'\+?\d{8,15}', '[REDACTED_PHONE]', str(record.msg))
        return True

def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        handler.setFormatter(formatter)
        handler.addFilter(PIIRedactionFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
