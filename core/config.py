# core/config.py
import os

class BaseConfig:
    # ในโปรดักชันควรตั้งเป็น ENV จริง
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'your_super_secret_key_admin')
    OWNER_SECRET_KEY = os.environ.get('OWNER_SECRET_KEY', 'your_super_secret_key_owner')
