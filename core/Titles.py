import math
import datetime
import requests
from geojson import Feature, FeatureCollection, Point
from threading import Thread
from core.Places import Places
import queue


class Titles(object):
    conf = {}

    def __init__(self, conf):
        self.conf = conf

    def num(self, zoom):
        return math.pow(2, zoom)

    def to_lon(self, x, zoom):
        return x / self.num(zoom) * 360.0 - 180.0

    def to_bb(self, zoom, x, y):
        result = {
            "lon_min": self.to_lon(x, zoom),
            "lon_max": self.to_lon(x + 1, zoom),
            "lat_max": self.to_lat(y, zoom),
            "lat_min": self.to_lat(y + 1, zoom)
        }
        return result

    def to_lat(self, y, zoom):
        n = math.pi * (1 - 2 * y / self.num(zoom))
        return math.degrees(math.atan(math.sinh(n)))

    # prod : preso in input da url
    # placeprefix : preso in input da url
    # params : contiene la data esatta
    # z : preso in input da url
    # x : '' ''
    # y : '' ''
    def get_weather_ex(self, prod, placeprefix, params, z, x, y):
        # setto la data esatta della chiamata
        if params['date'] is None:
            now = datetime.datetime.now()
            params['date'] = now.strftime("%Y%m%dZ%H00")

        # print "Date:"+str(params['date'])
        features = []

        # funzione effettuata dal singolo thread
        def do_stuff(q):
            while not q.empty():
                item = q.get()
                # print("ITEM : " + str(item))
                # print "Dequeued:"+str(item['id'])
                country = "IT"

                var = item['id']

                if item['id'].startswith("euro"):
                    country = var[4:6]

                url = self.conf['BASE_URL'] + "/products/" + prod + "/forecast/" + item['id'] + "?date=" + params['date']

                # print("Request:"+str(url))
                # text=requests.get(url).text.decode("utf-8")
                # print "<<"
                # print str(text)
                # print ">>"
                # data = simplejson.loads(text)

                data = requests.get(url).json()

                # print(data)
                # print("DATA GET_URL : " + str(data))
                if "forecast" in data:
                    # cLon = item['pos']['coordinates'][0] -- change
                    cLon = item['bbox']['coordinates'][0]
                    # cLat = item['pos']['coordinates'][1] -- change
                    cLat = item['bbox']['coordinates'][1]
                    feature = Feature(geometry=Point((cLon, cLat)))
                    # feature = Feature(geometry=Point((item['cLon'], item['cLat'])))
                    # feature["properties"] = {"id": item['id'], "name": item['name']['it'], "country": country} -- change
                    feature["properties"] = {"id": item['id'], "name": item['long_name']['it'], "country": country}

                    for key in data['forecast']:
                        feature["properties"][key] = data['forecast'][key]

                    # print("feature")
                    # print(feature)

                    features.append(feature)
                q.task_done()
            # print "Worker ended"

        # END do_staff()

        # creo un istanza di un luogo
        places = Places(self.conf)

        # da coordinata x,y,z calcolo la min,max si long,lat
        bb = self.to_bb(z, x, y)

        # creo un filtro matematico
        filter = []
        for part in placeprefix.split("-"):
            filter.append(str(part))

        options = {
            "filter": filter,
            "zoom": z
        }

        # ricerco i luoghi con tali coordinate
        items = places.get_places_by_bb(bb['lon_min'], bb['lat_min'], bb['lon_max'], bb['lat_max'], options)

        # print("id : " + items['id'])
        # print("long_name : " + items['long_name']['it'])
        # print("name : " + items['name']['it'])
        # print("bbox - type : " + items['bbox']['type'])
        # print("bbox - coordinates : " + str(items['bbox']['coordinates']))

        q = queue.Queue(maxsize=0)
        for item in items:
            # print("Queued:"+str(item['id']))
            q.put(item)

        # q = queue.Queue(maxsize=0)
        # q.put(items)

        # print("Elements of dict : " + str(items.__len__()))
        num_threads = items.__len__()
        if num_threads > self.conf['NUM_THREADS']:
            num_threads = int(self.conf['NUM_THREADS'])

        for i in range(num_threads):
            worker = Thread(target=do_stuff, args=(q,))
            worker.start()

        # worker = Thread(target=do_stuff, args=(q,))
        # worker.start()

        q.join()

        # print("FEAUTURE")
        # print(features)
        result = FeatureCollection(features)
        # print("RESAULT")
        # print(result)
        return result
