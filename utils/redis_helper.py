#功能是查询redis如果没有就去DB 最后结果是取出来相对应的object

from django.conf import settings
#from django_hbase.models import HBaseModel
from utils.redis_client import RedisClient
from utils.redis_serializer import DjangoModelSerializer
    # , HBaseModelSerializer

class RedisHelper:



    #
    # cache miss
    @classmethod
    def _load_iobjects_to_cache(cls, key, objects):
        conn = RedisClient.get_cnonection()
        serialized_list = []

        for object in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(object)
            serialized_list.append(serialized_data)

        if serialized_list:
            #     * rep push one by one
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)


    #when we call load_objects, we might face 2 situations,
    #1. cache hit. then we only need to use lrange to get all serialized data from cache.
    #then we will deserialize data and append them into a object list
    #finally return the list
    #2. cache miss, we need to use "_load_iobjects_to_cache", to push miss info into cache
    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_cnonection()

        if conn.exists(key):
            #cache hit
            #lrange是从左到右取出key对应value(list)
            serialized_list = conn.lrange(key, 0, -1)
            objects = []

            for serialized_data in serialized_list:
                deserialized_object = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_object)

            return objects

        #cache miss
        #需要写入cache
        cls._load_iobjects_to_cache(key, queryset)


    #load出来的时候 出来的是原本的objects data


    #push进去的时候 实际进去的是一个serialized过的object data


    #when we create a new object, we need to use this method to call "_load_iobjects_to_cache" to push it into cache
    #when we update a object, we need to serialize the new data info, and push back into cache
    @classmethod
    def push_objects(cls, key, object, queryset):
        conn = RedisClient.get_cnonection()
        if not conn.exists(key):
            cls._load_iobjects_to_cache(key, queryset)
            return
        serialized_data = DjangoModelSerializer.serialize(object)
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)

