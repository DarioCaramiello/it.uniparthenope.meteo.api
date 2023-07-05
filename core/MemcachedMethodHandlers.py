from time import strftime, gmtime
import hashlib  # hash function for 128bit encryption
import memcache


# request the resource from the cache
def get_resource(request_in, cache, use_pymemcache):
    if use_pymemcache is False:
        return None
    res_out = None
    m = hashlib.md5(request_in.url.encode('utf-8'))
    if m is not None:
        try:
            res_out = cache.get(m.hexdigest())
        except memcache.MemcacheError as e:
            print("[*] MemcacheError : " + str(e))
    return res_out


# set resource to cache
def set_resource(request_in, res, cache, use_pymemcache):
    if use_pymemcache is False:
        return
    m = hashlib.md5(request_in.url.encode('utf-8'))
    if m is not None:
        to_expire = (60 - int(strftime("%M", gmtime()))) * 60
        try:
            cache.set(m.hexdigest(), res, to_expire)
        except memcache.MemcacheError as e:
            print("[*] MemcacheError : " + str(e))


