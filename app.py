from flask import Flask
from apis import api
from pymemcache.client.base import Client
import memcache.errors


application = Flask(__name__)
api.init_app(application)

application.config.from_object(__name__)
application.config.from_envvar('APP_SETTINGS', silent=False)

# ------------------ Diskcached --------------------------
use_disk_cached = False

# ------------------ Pymemcache / Memcache ---------------
cache = None
use_pymemcache = False
try:
    cache = Client('memcached:11211')
    use_pymemcache = True
except memcache.errors.MemcacheError as memcache_error:
    print("[*]Memcached Error : " + str(memcache_error))



