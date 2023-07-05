import math
import calendar
import uuid
from PIL import Image
import urllib.parse as urllib
import urllib.request as urllib_request
import netCDF4
import numpy as np
import requests
import simplejson
import os.path
from flask import make_response
from core.Places import Places
from datetime import datetime, timedelta, time
from queue import Queue
from threading import Thread
import xmltodict


def windS(direction):
    if 11.25 <= direction < 33.75:
        return "NNE"
    if 33.75 <= direction < 56.25:
        return "NE"
    if 56.25 <= direction < 78.75:
        return "ENE"
    if 78.75 <= direction < 101.25:
        return "E"
    if 101.25 <= direction < 123.75:
        return "ESE"
    if 123.75 <= direction < 146.25:
        return "SE"
    if 146.25 <= direction < 168.75:
        return "SSE"
    if 168.75 <= direction < 191.25:
        return "S"
    if 191.25 <= direction < 213.75:
        return "SSW"
    if 213.75 <= direction < 236.25:
        return "SW"
    if 236.25 <= direction < 258.75:
        return "WSW"
    if 258.75 <= direction < 281.25:
        return "W"
    if 281.25 <= direction < 303.75:
        return "WNW"
    if 303.75 <= direction < 326.25:
        return "NW"
    if 326.25 <= direction < 348.75:
        return "NNW"
    if 348.75 <= direction < 359.9999:
        return "N"


def currS(direction):
    if 11.25 <= direction < 33.75:
        return "SSW"
    if 33.75 <= direction < 56.25:
        return "SW"
    if 56.25 <= direction < 78.75:
        return "WSW"
    if 78.75 <= direction < 101.25:
        return "W"
    if 101.25 <= direction < 123.75:
        return "WNW"
    if 123.75 <= direction < 146.25:
        return "NW"
    if 146.25 <= direction < 168.75:
        return "NNW"
    if 168.75 <= direction < 191.25:
        return "N"
    if 191.25 <= direction < 213.75:
        return "NNE"
    if 213.75 <= direction < 236.25:
        return "NE"
    if 236.25 <= direction < 258.75:
        return "ENE"
    if 258.75 <= direction < 281.25:
        return "E"
    if 281.25 <= direction < 303.75:
        return "ESE"
    if 303.75 <= direction < 326.25:
        return "SE"
    if 326.25 <= direction < 348.75:
        return "SSE"
    if 348.75 <= direction < 359.9999:
        return "S"


def iconText(current):
    wtext = [
        {
            "it": "Sereno",
            "en": "Clear"
        },
        {
            "it": "Poco nuvoloso",
            "en": "Partly Cloudy"
        },
        {
            "it": "Nuvoloso",
            "en": "Cloudy"
        },
        {
            "it": "Molto nuvoloso",
            "en": "Very Cloudy"
        },
        {
            "it": "Coperto",
            "en": "Covered"
        },
        {
            "it": "Rovesci",
            "en": "Showers"
        },
        {
            "it": "Pioggia",
            "en": "Rain"
        },
        {
            "it": "Forti piogge",
            "en": "Heavy Rains"
        }
    ]

    # print "iconText:"+str(current)

    crh = float(current['crh'])
    clf = float(current['clf'])
    date13 = current['date']
    if len(date13) == 11:
        date13 = date13 + "00"
    hhmm = date13[-4:]

    # print "----------------> date:"+str(date13)+"-->"+str(hhmm)

    if (hhmm >= "0500") and (hhmm <= "1800"):
        suf = '.png'
    else:
        suf = '_night.png'

    # print "suf: " + suf

    if crh < 0.1:
        if clf < .0625:
            return ('sunny' + suf), wtext[0]
        if clf < .1875:
            return ('cloudy1' + suf), wtext[1]
        if clf < .625:
            return ('cloudy2' + suf), wtext[2]
        if clf < .875:
            return ('cloudy4' + suf), wtext[3]
        return ('cloudy5' + suf), wtext[4]

    if crh < 2:
        return ('shower1' + suf), wtext[5]

    if crh < 10:
        return ('shower2' + suf), wtext[6]
    return ('shower3' + suf), wtext[7]


def knt2kmh(knt):
    return knt * 1.852


def windChill(t2c, ws10):
    wind = pow(knt2kmh(float(ws10)), 0.16)
    return round((13.12 + 0.6215 * t2c - 11.37 * wind + 0.3965 * t2c * wind))


#### CSVFY ####
def csvfy(data):
    result = ""
    timeseries = data['timeseries']
    fields = data['fields']
    keys = ['dateTime']
    for field in fields:
        if not 'dateTime' in field:
            keys.append(field)
    line = ""
    for key in keys:
        line = line + key + ";"
    result = line[:-1] + "\n"

    for item in timeseries:
        line = ""

        for key in keys:
            try:
                line = line + str(item[str(key)]) + ";"
            except:
                line = line + ";"

        result = result + line[:-1] + "\n"

    output = make_response(result)
    output.headers["Content-type"] = "text/csv"
    return output


def knt2Beaufort(d):
    if d < 1:
        return 0
    if d < 3:
        return 1
    if d < 6:
        return 2
    if d < 10:
        return 3
    if d < 16:
        return 4
    if d < 21:
        return 5
    if d < 27:
        return 6
    if d < 33:
        return 7
    if d < 40:
        return 8
    if d < 47:
        return 9
    if d < 55:
        return 10
    if d < 63:
        return 11
    return 12


class MeteoServices:
    default_domain = 'd01'
    default_place = 'reg15'
    default_output = 'gen'
    default_prod = 'wrf3'
    default_xdim = 1024
    default_ydim = 768
    default_run = 'not'
    config = {}
    path = ""
    __statusCode = {'200': {'code': '200', 'msg': 'OK'}, '205': {'code': '205', 'msg': 'No Content'},
                    '231': {'code': '231', 'msg': 'Info Not Available'}, '400': {'code': '400', 'msg': 'Bad Request'},
                    '401': {'code': '401', 'msg': 'Unauthorized'}, '404': {'code': '404', 'msg': 'Not Found'}}

    def __init__(self, config):
        self.config = config
        self.products = None
        self.maps = None
        self.legal = None
        with open(self.config["PRODUCTS"]) as f:
            self.products = simplejson.load(f)
        with open(self.config["MAPS"]) as f:
            self.maps = simplejson.load(f)
        with open(self.config["LEGAL"]) as f:
            self.legal = simplejson.load(f)

    def getMaps(self):
        return self.maps

    def printMaps(self):
        print(self.maps)

    def getThemes(self, prod):
        return self.maps['themes'][prod]

    def printThemes(self):
        for theme in self.maps['themes']:
            print(theme)

    def printProdsTheme(self, prod):
        for prod_item in self.maps['themes'][prod]:
            print(prod_item)

    def getProds(self, prod=None):
        result = {}
        if prod is None:
            result = self.products
        else:
            try:
                result = self.products[prod]
            except ValueError as e:
                print("[*] Value error : " + str(e))
        return result

    def printProducts(self):
        for item in self.products:
            print(item)

    def __getFullLink(self, url, fields):
        fields_string = ''
        for key, value in fields.iteritems():
            fields_string = fields_string + key + '=' + value + '&'
        fields_string = fields_string.rstrip('&')
        full_link = url + '?' + fields_string
        return full_link

    def __executeRequest(self, url):
        data = urllib_request.urlopen(url)
        data = data.read()

        if "Not Found" in data:
            return False

        if not data:
            return True
        else:
            return data

    def calc_boundaries(self, west_east_dim, south_north_dim, XLONG, XLAT):
        xlon_a = [XLONG[0, 0], XLONG[south_north_dim - 1, 0], XLONG[0, west_east_dim - 1],
                  XLONG[south_north_dim - 1, west_east_dim - 1]]

        # check for dateline
        ilon = 0
        if abs(xlon_a[0] - xlon_a[2]) > 180.: ilon = 1
        if abs(xlon_a[1] - xlon_a[3]) > 180.: ilon = 1

        abslatmin = np.array(XLAT).min()
        abslatmax = np.array(XLAT).max()
        abslonmin = 99999.
        abslonmax = -99999.
        for i in range(0, 4):
            if xlon_a[i] < 0.0 and ilon == 1:
                abslonmin = min(abslonmin, 360. + xlon_a[i])
                abslonmax = max(abslonmax, 360. + xlon_a[i])
            else:
                abslonmin = min(abslonmin, xlon_a[i])
                abslonmax = max(abslonmax, xlon_a[i])

        lat_min = float(abslatmin)
        lat_max = float(abslatmax)
        lon_min = float(abslonmin)
        lon_max = float(abslonmax)

        dxll = (lon_max - lon_min) / west_east_dim
        dyll = (lat_max - lat_min) / south_north_dim

        return lon_min, lat_min, lon_max, lat_max, round(dxll, 6), round(dyll, 6)

    def printSpecificProducts(self, prod):
        for item in self.products[prod]:
            print(item)

    def getFields(self, prod):
        result = {}
        if prod in self.products and 'fields' in self.products[prod]:
            result = self.products[prod]['fields']
        return result

    def getOutputs(self, prod):
        result = {}
        if prod in self.products and 'outputs' in self.products[prod]:
            result = self.products[prod]['outputs']
        return result

    def getProductAvail(self, params):
        places = Places(self.config)
        items = []
        prod = None
        place = None
        offset_pre = 1
        offset_post = 0
        timeref = None

        if params:
            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

            if 'offset_pre' in params:
                offset_pre = float(params['offset_pre'])

            if 'offset_pre' in params:
                offset_post = float(params['offset_post'])

        # Get the domain and the indeces of the place
        domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

        # Check if domain and indeces are correct
        if domain_indeces is not None:

            # Retrieve domain and indeces
            (domain, Jmin, Jmax, Imin, Imax) = domain_indeces

            def daterange(start_date, end_date):
                N = abs((end_date - start_date).days * 1440)
                for n in range(0, N, 10):
                    yield start_date + timedelta(n / 1440.0)

            def check_date(date):
                item = None
                dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(
                    date.hour, '02') + format(date.minute, '02')
                dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

                # :/storage/ccmmma/prometeo/data/opendap//rdr1/d04/archive/2023/04/19/rdr1_d04_20230419Z0650.nc
                url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config[
                    'HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"
                # print("URL:"+str(url))

                if os.path.isfile(url):
                    item = {"prod": prod, "domain": domain, "place": place, "date": dateTime}
                return item

            if timeref is None:
                utc_now = datetime.utcnow()
                utc_now = datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour, 0, 0)
                time_delta_pre = timedelta(minutes=offset_pre * 1440)
                time_delta_post = timedelta(minutes=offset_post * 1440)
                start_date = utc_now - time_delta_pre
                end_date = utc_now + time_delta_post

                for date in daterange(start_date, end_date):
                    item = check_date(date)
                    if item is not None:
                        items.append(item)
            else:
                year = int(timeref[:4])
                month = int(timeref[4:6])
                day = int(timeref[6:8])
                hour = int(timeref[9:11])
                if len(timeref) == 13:
                    minute = int(timeref[11:13])
                else:
                    minute = 0

                date = datetime(year, month, day, hour, minute)
                item = check_date(date)
                if item is not None:
                    items.append(item)
        return items

    def getLegalDisclaimer(self, options=None):
        lang = "en-US"
        if options is not None:
            if "lang" in options and options['lang'] is not None:
                lang = options['lang']

        result = {
            "i18n": {
                lang: {
                    "disclaimer": self.legal["i18n"][lang]['disclaimer']
                }
            }
        }
        return result

    def getLegalPrivacy(self, options=None):
        lang = "en-US"
        if options is not None:
            if "lang" in options and options['lang'] is not None:
                lang = options['lang']

        result = {
            "i18n": {
                lang: {
                    "privacy": self.legal["i18n"][lang]['privacy']
                }
            }
        }
        return result

    def getProductAvailCalendar(self, params):
        places = Places(self.config)
        calendar_items = []
        baseUrl = ""
        prod = "wrf5"
        start = None
        end = None
        timeZone = "UTC"

        start_date = None
        end_date = None

        if params:
            if 'baseUrl' in params and params['baseUrl'] is not None:
                baseUrl = params['baseUrl']

            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'start' in params and params['start'] is not None:
                start = params['start']

            if 'end' in params and params['end'] is not None:
                end = params['end']

            if 'timeZone' in params and params['timeZone'] is not None:
                timeZone = params['timeZone']

        if start is None:
            utc_now = datetime.utcnow()
            start_date = datetime(utc_now.year, utc_now.month, 1, 0, 0, 0)
        else:
            # 2020-04-15T10:30:00+00:00
            year = int(start[:4])
            month = int(start[5:7])
            day = int(start[8:10])
            hour = int(start[11:13])
            minute = int(start[14:16])

            # print start[:4], start[5:7], start[8:10], start[11:13], start[14:16]

            start_date = datetime(year, month, day, hour, minute)

        if end is None:
            utc_now = datetime.utcnow()
            lastDay = calendar.monthrange(utc_now.year, utc_now.month)[1]
            end_date = datetime(utc_now.year, utc_now.month, lastDay, 23, 59, 59)
        else:
            # 2020-04-15T10:30:00+00:00
            year = int(end[:4])
            month = int(end[5:7])
            day = int(end[8:10])
            hour = int(end[11:13])
            minute = int(end[14:16])

            end_date = datetime(year, month, day, hour, minute)

        # Get the domain and the indeces of the place
        domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

        # Check if domain and indeces are correct
        if domain_indeces is not None:

            # Retrieve domain and indeces
            (domain, Jmin, Jmax, Imin, Imax) = domain_indeces

            def daterange(start_date, end_date):
                N = abs((end_date - start_date).days * 1440)
                for n in range(0, N, 10):
                    yield start_date + timedelta(n / 1440.0)

            def check_date(date):
                item = None
                dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(
                    date.hour, '02') + format(date.minute, '02')
                dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

                sources = []
                url = self.config[
                          'BASE_PATH'] + "/" + prod + "/" + domain + "/history/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"
                if os.path.isfile(url):
                    sources.append("history")

                url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config[
                    'ARCHIVE'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"
                if os.path.isfile(url):
                    sources.append("archive")

                if len(sources) > 0:
                    item = {"prod": prod, "domain": domain, "place": place, "date": dateTime, "sources": sources}
                return item

            for date in daterange(start_date, end_date):
                item = check_date(date)
                if item is not None:

                    calendar_dateTime_start = format(date.year, '04') + "-" + format(date.month, '02') + "-" + format(
                        date.day, '02') + "T" + format(date.hour, '02') + ":" + format(date.minute, '02') + ":00+00:00"

                    minute_end = 0
                    if "rdr1" in prod or "rdr2" in prod:
                        minute_end = date.minute + 9
                    else:
                        minute_end = date.minute + 59

                    calendar_dateTime_end = format(date.year, '04') + "-" + format(date.month, '02') + "-" + format(
                        date.day, '02') + "T" + format(date.hour, '02') + ":" + format(minute_end, '02') + ":00+00:00"

                    title = item["domain"]
                    if "history" in item["sources"]: title = title + "/H"
                    if "archive" in item["sources"]: title = title + "/A"

                    calendar_item = {
                        "groupId": item["prod"],
                        "title": title,
                        "start": calendar_dateTime_start,
                        "end": calendar_dateTime_end,
                        "url": baseUrl + "&prod=" + item["prod"] + "&place=" + item["place"] + "&date=" + item["date"]
                    }
                    calendar_items.append(calendar_item)
        return calendar_items


    def modelOutput(self, params=None):
        retval = {}

        places = Places(self.config)
        prod = self.default_prod
        place = self.default_place

        timeref = None
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0

        # print "params in modeloutput:"+str(params)

        if params:
            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

        if timeref is None:
            date = datetime.utcnow()
            year = date.year
            month = date.month
            day = date.day
            hour = int(round(date.hour + date.minute / 60.0))
            minute = 0
        else:
            # print "Date is provided"
            year = int(timeref[:4])
            month = int(timeref[4:6])
            day = int(timeref[6:8])
            hour = int(timeref[9:11])
            if len(timeref) == 13:
                minute = int(timeref[11:13])

        # print "Place:"+str(place)
        date = datetime(year, month, day, hour, minute)
        # print "date:"+str(date)

        # Get the domain and the indeces of the place
        domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

        # Check if domain and indeces are correct
        if domain_indeces is not None:
            # Retrieve domain and indeces
            (domain, Jmin, Jmax, Imin, Imax) = domain_indeces
            # print("Jmin : " + str(Jmin))
            # print("Jmax : " + str(Jmax))
            # print("Imin : " + str(Imin))
            # print("Imax : " + str(Imax))

            # Set the dateTime
            dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(date.hour, '02') + format(date.minute, '02')

            dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')
            url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config['HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"

            retval = {}

            # Check if the file exists
            dataset = None

            try:
                # Open the data file
                dataset = netCDF4.Dataset(url)
            except Exception as e:
                print("[*] netCDF4 error : " + str(e))

            if dataset is not None:
                retval['forecast'] = {"dateTime": dateTime}

                retval['forecast']['link'] = "product=" + prod + "&place=" + place + "&date=" + dateTime
                iDate = None
                try:
                    iDate = dataset.IDATE
                except Exception as e:
                    print("[*] dataset.IDATA error : " + str(e))

                if iDate is not None:
                    retval['forecast']["iDate"] = iDate

                # Check if wrf5 have to be processed
                if "wrf5" in prod:
                    t2c = round(float(np.mean(dataset.variables['T2C'][0, Jmin:Jmax, Imin:Imax])), 1)
                    crh = round(float(np.mean(dataset.variables['DELTA_RAIN'][0, Jmin:Jmax, Imin:Imax])), 1)
                    # t2c = round(np.mean(dataset.variables['T2C'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # crh = round(np.mean(dataset.variables['DELTA_RAIN'][0, Jmin:Jmax, Imin:Imax]), 1)
                    if crh < 0:
                        crh = 0
                    crd = 0
                    try:
                        crd = round(float(np.mean(dataset.variables['DAILY_RAIN'][0, Jmin:Jmax, Imin:Imax])), 1)
                        # crd = float(np.mean(dataset.variables['DAILY_RAIN'][0, Jmin:Jmax, Imin:Imax]), 1)
                        if crd < 0:
                            crd = 0
                    except:
                        pass

                    try:
                        swe = round(float(np.mean(dataset.variables['HOURLY_SWE'][0, Jmin:Jmax, Imin:Imax])), 1)
                        # swe = round(np.mean(dataset.variables['HOURLY_SWE'][0, Jmin:Jmax, Imin:Imax]), 1)
                        if math.isnan(swe) or swe < 0:
                            swe = 0
                        retval['forecast']['swe'] = swe
                    except:
                        pass

                    slp = round(float(np.mean(dataset.variables['SLP'][0, Jmin:Jmax, Imin:Imax])), 1)
                    clf = round(float(np.mean(dataset.variables['CLDFRA_TOTAL'][0, Jmin:Jmax, Imin:Imax])), 2)
                    rh2 = round(float(np.mean(dataset.variables['RH2'][0, Jmin:Jmax, Imin:Imax])), 1)
                    u10m = round(float(np.mean(dataset.variables['U10M'][0, Jmin:Jmax, Imin:Imax])), 2)
                    v10m = round(float(np.mean(dataset.variables['V10M'][0, Jmin:Jmax, Imin:Imax])), 2)
                    ws10 = round(float(np.mean(dataset.variables['WSPD10'][0, Jmin:Jmax, Imin:Imax])), 1)
                    wd10 = round(float(np.mean(dataset.variables['WDIR10'][0, Jmin:Jmax, Imin:Imax])), 1)
                    dws10 = round(float(np.mean(dataset.variables['DELTA_WSPD10'][0, Jmin:Jmax, Imin:Imax])), 1)
                    dwd10 = round(float(np.mean(dataset.variables['DELTA_WDIR10'][0, Jmin:Jmax, Imin:Imax])), 1)

                    # slp = round(np.mean(dataset.variables['SLP'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # clf = round(np.mean(dataset.variables['CLDFRA_TOTAL'][0, Jmin:Jmax, Imin:Imax]), 2)
                    # rh2 = round(np.mean(dataset.variables['RH2'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # u10m = round(np.mean(dataset.variables['U10M'][0, Jmin:Jmax, Imin:Imax]), 2)
                    # v10m = round(np.mean(dataset.variables['V10M'][0, Jmin:Jmax, Imin:Imax]), 2)
                    # ws10 = round(np.mean(dataset.variables['WSPD10'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # wd10 = round(np.mean(dataset.variables['WDIR10'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # dws10 = round(np.mean(dataset.variables['DELTA_WSPD10'][0, Jmin:Jmax, Imin:Imax]), 1)
                    #dwd10 = round(np.mean(dataset.variables['DELTA_WDIR10'][0, Jmin:Jmax, Imin:Imax]), 1)

                    try:
                        u300 = round(float(np.mean(dataset.variables['U300'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u300 = round(np.mean(dataset.variables['U300'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u300):
                            retval['forecast']['u300'] = u300
                    except:
                        pass

                    try:
                        v300 = round(float(np.mean(dataset.variables['V300'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v300 = round(np.mean(dataset.variables['V300'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v300):
                            retval['forecast']['v300'] = v300
                    except:
                        pass

                    try:
                        rh300 = round(float(np.mean(dataset.variables['RH300'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh300 = round(np.mean(dataset.variables['RH300'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh300):
                            retval['forecast']['rh300'] = rh300
                    except:
                        pass

                    try:
                        tc300 = round(float(np.mean(dataset.variables['TC300'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc300 = round(np.mean(dataset.variables['TC300'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc300):
                            retval['forecast']['tc300'] = tc300
                    except:
                        pass

                    try:
                        u500 = round(float(np.mean(dataset.variables['U500'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u500 = round(np.mean(dataset.variables['U500'][0, Jmin:Jmax, Imin:Imax]), 2)
                        print("U500 : " + str(u500))
                        if not math.isnan(u500[:]):
                            retval['forecast']['u500'] = u500
                    except:
                        pass

                    try:
                        v500 = round(float(np.mean(dataset.variables['V500'][0, Jmin:Jmax, Imin:Imax])), 2)
                        print("V500 : " + str(v500[:]))
                        # v500 = round(np.mean(dataset.variables['V500'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v500):
                            retval['forecast']['v500'] = v500
                    except:
                        pass

                    try:
                        rh500 = round(float(np.mean(dataset.variables['RH500'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh500 = round(np.mean(dataset.variables['RH500'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh500):
                            retval['forecast']['rh500'] = rh500
                    except:
                        pass

                    try:
                        tc500 = round(float(np.mean(dataset.variables['TC500'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc500 = round(np.mean(dataset.variables['TC500'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc500):
                            retval['forecast']['tc500'] = tc500
                    except:
                        pass

                    try:
                        u700 = round(float(np.mean(dataset.variables['U700'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u700 = round(np.mean(dataset.variables['U700'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u700):
                            retval['forecast']['u700'] = u700
                    except:
                        pass

                    try:
                        v700 = round(float(np.mean(dataset.variables['V700'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v700 = round(np.mean(dataset.variables['V700'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v700):
                            retval['forecast']['v700'] = v700
                    except:
                        pass

                    try:
                        rh700 = round(float(np.mean(dataset.variables['RH700'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh700 = round(np.mean(dataset.variables['RH700'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh700):
                            retval['forecast']['rh700'] = rh700
                    except:
                        pass

                    try:
                        tc700 = round(float(np.mean(dataset.variables['TC700'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc700 = round(np.mean(dataset.variables['TC700'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc700):
                            retval['forecast']['tc700'] = tc700
                    except:
                        pass

                    try:
                        u850 = round(float(np.mean(dataset.variables['U850'][0, Jmin:Jmax, Imin:Imax])), 2)
                        if not math.isnan(u850):
                            retval['forecast']['u850'] = u850
                    except:
                        pass

                    try:
                        v850 = round(float(np.mean(dataset.variables['V850'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v850 = round(np.mean(dataset.variables['V850'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v850):
                            retval['forecast']['v850'] = v850
                    except:
                        pass

                    try:
                        rh850 = round(float(np.mean(dataset.variables['RH850'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh850 = round(np.mean(dataset.variables['RH850'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh850):
                            retval['forecast']['rh850'] = rh850
                    except:
                        pass

                    try:
                        tc850 = round(float(np.mean(dataset.variables['TC850'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc850 = round(np.mean(dataset.variables['TC850'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc850):
                            retval['forecast']['tc850'] = tc850
                    except:
                        pass

                    try:
                        u925 = round(float(np.mean(dataset.variables['U925'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u925 = round(np.mean(dataset.variables['U925'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u925):
                            retval['forecast']['u925'] = u925
                    except:
                        pass

                    try:
                        v925 = round(float(np.mean(dataset.variables['V925'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v925 = round(np.mean(dataset.variables['V925'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v925):
                            retval['forecast']['v925'] = v925
                    except:
                        pass

                    try:
                        rh925 = round(float(np.mean(dataset.variables['RH925'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh925 = round(np.mean(dataset.variables['RH925'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh925):
                            retval['forecast']['rh925'] = rh925
                    except:
                        pass

                    try:
                        tc925 = round(float(np.mean(dataset.variables['TC925'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc925 = round(np.mean(dataset.variables['TC925'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc925):
                            retval['forecast']['tc925'] = tc925
                    except:
                        pass

                    try:
                        u950 = round(float(np.mean(dataset.variables['U950'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u950 = round(np.mean(dataset.variables['U950'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u950):
                            retval['forecast']['u950'] = u950
                    except:
                        pass

                    try:
                        v950 = round(float(np.mean(dataset.variables['V950'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v950 = round(np.mean(dataset.variables['V950'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v950):
                            retval['forecast']['v950'] = v950
                    except:
                        pass

                    try:
                        rh950 = round(float(np.mean(dataset.variables['RH950'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh950 = round(np.mean(dataset.variables['RH950'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh950):
                            retval['forecast']['rh950'] = rh950
                    except:
                        pass

                    try:
                        tc950 = round(float(np.mean(dataset.variables['TC950'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc950 = round(np.mean(dataset.variables['TC950'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc950):
                            retval['forecast']['tc950'] = tc950
                    except:
                        pass

                    try:
                        u975 = round(float(np.mean(dataset.variables['U975'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u975 = round(np.mean(dataset.variables['U975'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u975):
                            retval['forecast']['u975'] = u975
                    except:
                        pass

                    try:
                        v975 = round(float(np.mean(dataset.variables['V975'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v975 = round(np.mean(dataset.variables['V975'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v975):
                            retval['forecast']['v975'] = v975
                    except:
                        pass

                    try:
                        rh975 = round(float(np.mean(dataset.variables['RH975'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh975 = round(np.mean(dataset.variables['RH975'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh975):
                            retval['forecast']['rh975'] = rh975
                    except:
                        pass

                    try:
                        tc975 = round(float(np.mean(dataset.variables['TC975'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc975 = round(np.mean(dataset.variables['TC975'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc975):
                            retval['forecast']['tc975'] = tc975
                    except:
                        pass

                    try:
                        u1000 = round(float(np.mean(dataset.variables['U1000'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # u1000 = round(np.mean(dataset.variables['U1000'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(u1000):
                            retval['forecast']['u1000'] = u1000
                    except:
                        pass

                    try:
                        v1000 = round(float(np.mean(dataset.variables['V1000'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # v1000 = round(np.mean(dataset.variables['V1000'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(v1000):
                            retval['forecast']['v1000'] = v1000
                    except:
                        pass

                    try:
                        rh1000 = round(float(np.mean(dataset.variables['RH100'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # rh1000 = round(np.mean(dataset.variables['RH100'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(rh1000):
                            retval['forecast']['rh1000'] = rh1000
                    except:
                        pass

                    try:
                        tc1000 = round(float(np.mean(dataset.variables['TC1000'][0, Jmin:Jmax, Imin:Imax])), 2)
                        # tc1000 = round(np.mean(dataset.variables['TC1000'][0, Jmin:Jmax, Imin:Imax]), 2)
                        if not math.isnan(tc1000):
                            retval['forecast']['tc1000'] = tc1000
                    except:
                        pass

                    retval['forecast']['t2c'] = t2c
                    retval['forecast']['rh2'] = rh2
                    retval['forecast']['clf'] = clf
                    retval['forecast']['crh'] = crh
                    retval['forecast']['crd'] = crd
                    retval['forecast']['slp'] = slp
                    retval['forecast']['wd10'] = wd10
                    retval['forecast']['ws10'] = ws10
                    retval['forecast']['dwd10'] = dwd10
                    retval['forecast']['dws10'] = dws10
                    retval['forecast']['u10m'] = u10m
                    retval['forecast']['v10m'] = v10m
                    retval['forecast']['ws10k'] = round(ws10 * 3.6, 1)
                    retval['forecast']['ws10n'] = round(ws10 * 1.94384449, 1)
                    retval['forecast']['ws10b'] = knt2Beaufort(retval['forecast']['ws10n'])
                    retval['forecast']['wchill'] = round(windChill(t2c, ws10), 1)
                    retval['forecast']['winds'] = windS(wd10)

                    try:
                        current = {
                            "date": dateTime,
                            "crh": retval['forecast']["crh"],
                            "clf": retval['forecast']["clf"]
                        }
                        retval['forecast']['icon'], retval['forecast']['text'] = iconText(current)
                    except:
                        pass

                elif "rms3" in prod:
                    print("rms3")
                    sst = np.nanmean(dataset.variables['temp'][0, 0, Jmin:Jmax, Imin:Imax])
                    sss = np.nanmean(dataset.variables['salt'][0, 0, Jmin:Jmax, Imin:Imax])
                    u = np.nanmean(dataset.variables['u'][0, 0, Jmin:Jmax, Imin:Imax])
                    v = np.nanmean(dataset.variables['v'][0, 0, Jmin:Jmax, Imin:Imax])
                    scm = (u * u + v * v) ** .5
                    scd = math.atan2(v, u) / math.pi * 180
                    if scd < 0:
                        scd = scd + 360

                    retval['forecast']['scm'] = round(scm, 2)
                    retval['forecast']['scd'] = round(scd, 1)
                    retval['forecast']['sst'] = round(float(sst), 1)
                    retval['forecast']['sss'] = round(float(sss), 2)
                    retval['forecast']['scs'] = currS(scd)

                elif "wcm3" in prod:
                    print("wcm3")
                    con = int(round(np.amax(dataset.variables['conc'][0, 0, Jmin:Jmax, Imin:Imax]), 0))

                    sts = 0
                    if 18 < con <= 230:
                        sts = 1
                    elif 230 < con <= 700:
                        sts = 2
                    elif 700 < con <= 4600:
                        sts = 3
                    elif 4600 < con <= 46000:
                        sts = 4
                    elif con > 46000:
                        sts = 5

                    retval['forecast']['sts'] = sts
                    retval['forecast']['con'] = con
                elif "aiq3" in prod:
                    mci = int(round(np.amax(dataset.variables['class_predict'][0, Jmin:Jmax, Imin:Imax]), 0))
                    retval['forecast']['mci'] = mci

                elif "ww33" in prod:
                    hs = np.nanmean(dataset.variables['hs'][0, Jmin:Jmax, Imin:Imax])
                    lm = np.nanmean(dataset.variables['lm'][0, Jmin:Jmax, Imin:Imax])
                    fp = np.nanmean(dataset.variables['fp'][0, Jmin:Jmax, Imin:Imax])
                    dir = np.nanmean(dataset.variables['dir'][0, Jmin:Jmax, Imin:Imax])
                    period = np.nanmean(dataset.variables['period'][0, Jmin:Jmax, Imin:Imax])
                    retval['forecast']['hs'] = round(float(hs), 2)
                    retval['forecast']['lm'] = round(float(lm), 2)
                    retval['forecast']['fp'] = round(float(fp), 4)
                    retval['forecast']['dir'] = round(float(dir), 1)
                    retval['forecast']['period'] = round(float(period), 2)

                elif "rdr1" in prod or "rdr2" in prod:
                    ref = round(float(np.mean(dataset.variables['reflectivity'][0, Jmin:Jmax, Imin:Imax])), 1)
                    rain = round(float(np.mean(dataset.variables['rain'][0, Jmin:Jmax, Imin:Imax])), 1)
                    mask = round(float(np.mean(dataset.variables['mask'][Jmin:Jmax, Imin:Imax])), 1)
                    # ref = round(np.mean(dataset.variables['reflectivity'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # rain = round(np.mean(dataset.variables['rain'][0, Jmin:Jmax, Imin:Imax]), 1)
                    # mask = round(np.mean(dataset.variables['mask'][Jmin:Jmax, Imin:Imax]), 1)
                    retval['forecast']['ref'] = ref
                    retval['forecast']['rain'] = rain
                    retval['forecast']['mask'] = mask

                dataset.close()

                retval['result'] = "ok"

                if "opt" in params:
                    if "place" in params['opt']:
                        retval['place'] = places.get_place_by_id(place, params)
                    if "fields" in params['opt']:
                        retval['fields'] = self.products[prod]['fields']
            else:
                retval['result'] = "error"
                retval['details'] = "Data not available"
        else:
            retval['result'] = "error"
            retval['details'] = "Place not indexed"
        return retval

    # def MakeControlFile(self, prod, dataset, control_file, date, months):
    def MakeControlFile(self, prod, dataset, date, months, url):

        control_file = """
        dset """ + url + """
        dtype netcdf"""

        if "rdr1" in prod or "rdr2" in prod:
            XLONG = dataset.variables["lon"][::]
            XLAT = dataset.variables["lat"][::]
            south_north_dim = len(XLAT)
            west_east_dim = len(XLONG[0])
            (lon_min, lat_min, lon_max, lat_max, dxll, dyll) = self.calc_boundaries(west_east_dim, south_north_dim,
                                                                                    XLONG, XLAT)
            control_file += """
            undef -999000000
            TITLE Weather Radar Output Grid: Time, bottom_top, south_north, west_eastx
            def """ + str(west_east_dim) + """ linear """ + str(lon_min) + """   """ + str(dxll) + """
            ydef  """ + str(south_north_dim) + """ linear   """ + str(lat_min) + """   """ + str(dyll) + """
            zdef  30 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """ 1hr""" + "\n"

        if "wcm3" in prod:
            ipoints = len(dataset.dimensions['longitude'])
            jpoints = len(dataset.dimensions['latitude'])
            lon0 = dataset.variables["longitude"][0]
            lat0 = dataset.variables["latitude"][0]
            lon1 = dataset.variables["longitude"][-1]
            lat1 = dataset.variables["latitude"][-1]

            dxll = (lon1 - lon0) / ipoints
            dyll = (lat1 - lat0) / jpoints

            control_file += """
            undef 1.0e+37f 
            TITLE WACOMM Output Grid: Time, bottom_top, south_north, west_east
            xdef """ + str(ipoints) + """ linear  """ + str(lon0) + """   """ + str(dxll) + """
            ydef """ + str(jpoints) + """ linear  """ + str(lat0) + """   """ + str(dyll) + """
            zdef  11 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """ 1hr""" + "\n"

        if "aiq3" in prod:
            ipoints = len(dataset.dimensions['longitude'])
            jpoints = len(dataset.dimensions['latitude'])
            lon0 = dataset.variables["longitude"][0]
            lat0 = dataset.variables["latitude"][0]
            lon1 = dataset.variables["longitude"][-1]
            lat1 = dataset.variables["latitude"][-1]
            dxll = (lon1 - lon0) / ipoints
            dyll = (lat1 - lat0) / jpoints

            control_file += """
            undef 1.0e+37f
            TITLE AIQUAM Output Grid: Time, bottom_top, south_north, west_east
            xdef """ + str(ipoints) + """ linear  """ + str(lon0) + """   """ + str(dxll) + """
            ydef """ + str(jpoints) + """ linear  """ + str(lat0) + """   """ + str(dyll) + """
            zdef  11 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """1hr""" + "\n"

        if "rms3" in prod:
            ipoints = len(dataset.dimensions['longitude'])
            jpoints = len(dataset.dimensions['latitude'])
            lon0 = dataset.variables["longitude"][0]
            lat0 = dataset.variables["latitude"][0]
            lon1 = dataset.variables["longitude"][-1]
            lat1 = dataset.variables["latitude"][-1]

            dxll = (lon1 - lon0) / ipoints
            dyll = (lat1 - lat0) / jpoints

            control_file += """
            undef 1.e+37
            TITLE ROMS Output Grid: Time, bottom_top, south_north, west_east
            xdef """ + str(ipoints) + """ linear  """ + str(lon0) + """   """ + str(dxll) + """
            ydef """ + str(jpoints) + """ linear  """ + str(lat0) + """   """ + str(dyll) + """
            zdef  11 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """ 1hr""" + "\n"

        if "ww33" in prod:
            ipoints = len(dataset.dimensions['longitude'])
            jpoints = len(dataset.dimensions['latitude'])
            lon0 = dataset.variables["longitude"][0]
            lat0 = dataset.variables["latitude"][0]
            lon1 = dataset.variables["longitude"][-1]
            lat1 = dataset.variables["latitude"][-1]

            dxll = (lon1 - lon0) / ipoints
            dyll = (lat1 - lat0) / jpoints

            control_file += """
            undef 1.e+37
            TITLE WWatch3 Output Grid: Time, bottom_top, south_north, west_east
            xdef """ + str(ipoints) + """ linear  """ + str(lon0) + """   """ + str(dxll) + """
            ydef """ + str(jpoints) + """ linear  """ + str(lat0) + """   """ + str(dyll) + """
            zdef   1 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """ 1hr""" + "\n"

        if "wrf5" in prod:
            ipoints = len(dataset.dimensions['longitude'])
            jpoints = len(dataset.dimensions['latitude'])
            lon0 = dataset.variables["longitude"][0]
            lat0 = dataset.variables["latitude"][0]
            lon1 = dataset.variables["longitude"][-1]
            lat1 = dataset.variables["latitude"][-1]
            dxll = (lon1 - lon0) / ipoints
            dyll = (lat1 - lat0) / jpoints
            control_file += """
            undef 1.e30
            title  OUTPUT FROM WRF V3.9.1 MODEL
            xdef """ + str(ipoints) + """ linear  """ + str(lon0) + """   """ + str(dxll) + """
            ydef """ + str(jpoints) + """ linear  """ + str(lat0) + """   """ + str(dyll) + """
            zdef  27 linear 1 1
            tdef   1 linear """ + format(date.hour, '02') + """:""" + format(date.minute, '02') + """Z""" + format(
                date.day, '02') + months[date.month - 1] + format(date.year, '04') + """ 1hr""" + "\n"

        control_file_final = ""

        for x in control_file.split('\n'):
            string = x.strip() + '\n'
            control_file_final += string

        control_file = control_file_final

        with open("/home/d.caramiello/dev/it.uniparthenope.meteo.api/vars-control-file/vars_" + prod + ".txt") as file_vars:
            data_text = file_vars.read()
            file_vars.close()

        control_file += data_text
        return control_file

    # MakePlotImage(minLon, maxLon, minLat, maxLat, place, domain, prod, str(width), str(height))

    def ModelPlotUrlOrImage(self, use_disk_cached=True, params=None):

        months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        retval = {}

        places = Places(self.config)
        prod = self.default_prod
        output = self.default_output
        place = self.default_place
        width = self.default_xdim
        height = self.default_ydim

        timeref = None
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0

        bars = 'false'
        if params:
            if 'opt' in params and params['opt'] is not None:
                if "bars" in params['opt']:
                    bars = 'true'
            if 'width' in params and params['width'] is not None:
                width = int(params['width'])

            if 'height' in params and params['height'] is not None:
                height = int(params['height'])

            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'output' in params and params['output'] is not None:
                output = params['output']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

        if timeref is None:
            # print "get current utc"
            date = datetime.utcnow()
            year = date.year
            month = date.month
            day = date.day
            hour = int(round(date.hour + date.minute / 60.0))
            minute = 0
        else:
            # print "Date is provided"
            year = int(timeref[:4])
            month = int(timeref[4:6])
            day = int(timeref[6:8])
            hour = int(timeref[9:11])
            if len(timeref) == 13:
                minute = int(timeref[11:13])

        dry = str(params['dry'])

        date = datetime(year, month, day, hour, minute)

        # Get place data
        params1 = {'id': place, 'filter': None, 'prod': prod}

        # Set the dateTime
        dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(date.hour, '02') + format(date.minute, '02')

        dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

        imageName = "plt_" + place + "_" + prod + "_" + dateTime + "_" + output + "_" + str(width) + "x" + \
                    str(height) + ".png"

        relativePath = "plt/" + place + "/" + prod + "/" + dateTimePath

        try:
            os.makedirs(self.config['BASE_PRODUCTS'] + "/" + relativePath)
        except OSError as e:
            print(str(e))

        imagePath = self.config['BASE_PRODUCTS'] + "/" + relativePath + "/" + imageName
        imageUrl = self.config['PUB_URL'] + "/" + relativePath + "/" + imageName

        # Check if the file already exists and it is valid
        if use_disk_cached is False or os.path.isfile(imagePath) is False or (os.path.isfile(imagePath) is True and (time.time() - os.path.getmtime(imagePath)) > 86400):

            # imagePath=self.cfg['NOIMAGE_PATH']
            placeData = places.get_place_by_id(place, params)

            if placeData is not None:

                # Get the domain and the indices of the place
                domain_indices = places.get_domain_and_indeces_by_product_and_place(prod, place)

                # print("domain_indeces:" + str(domain_indeces))

                # Check if domain and indeces are correct
                if domain_indices is not None:

                    # Retrieve domain and indeces
                    (domain, Jmin, Jmax, Imin, Imax) = domain_indices

                    minLon = placeData["minLon"]
                    minLat = placeData["minLat"]
                    maxLon = placeData["maxLon"]
                    maxLat = placeData["maxLat"]

                    # print("minLon : " + str(minLon) + " -- maxLon : " + str(maxLon))
                    # print("minLat : " + str(minLat) + " -- maxLat : " + str(maxLat))

                    # Set the local path of the data file
                    # url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config['HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"
                    url = self.config['BASE_PATH'] + prod + "/" + domain + "/" + self.config['HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"
                    dataset = None
                    try:
                        dataset = netCDF4.Dataset(url)
                    except Exception as e:
                        print("[*] Error open the data file : " + str(e))
                        imagePath = self.config['NOIMAGE_PATH']
                        imageUrl = self.config['NOIMAGE_URL']

                    if dataset is not None:
                        controlFile = self.MakeControlFile(params['prod'], dataset, date, months, url)
                        dataset.close()

                        tempdir = "/home/d.caramiello/dev/it.uniparthenope.meteo.api/tmp/grads_" + prod + "_" + str(uuid.uuid4())

                        try:
                            os.makedirs(tempdir)
                        except OSError as e:
                            print("[*]  makedirs Error : " + str(e))

                        controlFileName = tempdir + "/controlfile.ctl"

                        with open(controlFileName, "w") as file:
                            file.write(controlFile)
                            file.close()

                        script = self.config['GRADS_SCRIPT']

                        # environment = "/home/ccmmma/prometeo/opt/ccmmmaapi/sourceme-grads-2.2.1"
                        environment = "/home/d.caramiello/dev/it.uniparthenope.meteo.api/sourceme-grads-2.2.1"
                        label = placeData["long_name"]["it"]
                        command = 'grads -lbc "' + script + " " + controlFileName + " " + str(minLon) + " " + str(minLat) + " " + str(maxLon) + " " + str(maxLat) + " " + place + " " + domain + " " + prod + " " + output + " " + str(width) + " " + str(height) + " " + imagePath + " " + tempdir + " " + bars + " " + label + '"'
                        os.system(". " + environment + ";" + command)
                        # print("minLon : " + str(minLon))
                        # print("maxLon : " + str(maxLon))
                        # print("minLat : " + str(minLat))
                        # print("maxLat : " + str(maxLat))
                        # print("place : " + str(place))
                        # print("domain : " + str(domain))
                        # print("prod : " + str(prod))
                        # print("output : " + str(output))
                        # print("width : " + str(width))
                        # print("height : " + str(height))
                        # print("imagePath : " + str(imagePath))
                        # print("tempdir : " + str(tempdir))
                        # print("bars : " + str(bars))
                        # print("label : " + str(label))
                        # shutil.rmtree(tempdir)
            else:
                # The place is not available
                imagePath = self.config['NOIMAGE_PATH']
                imageUrl = self.config['NOIMAGE_URL']

        retval['link'] = imageUrl

        if dry.lower() == "false":
            try:
                with open(imagePath, 'rb') as content_file:
                    retval = content_file.read()
                    content_file.close()
            except Exception as e:
                print("[*] Error open imagePath : " + str(e))
                imagePath = self.config['NOIMAGE_PATH']
                imageUrl = self.config['NOIMAGE_URL']
        print(str(url))
        return retval, imageName

    def getlegenddata(self, prod, position, output, params=None):

        data = None
        width = self.default_xdim
        height = self.default_ydim
        lang = "en-US"

        if params is not None:
            if "lang" in params and params['lang'] is not None:
                lang = params['lang']

            if 'width' in params and params['width'] is not None:
                width = int(params['width'])

            if 'height' in params and params['height'] is not None:
                height = int(params['height'])

        # Generate a bitmap
        imgName = "legend_" + prod + "_" + position + "_" + output + "_" + str(width) + "x" + str(
            height) + ":" + lang + ".png"
        # imgPath = self.config['BASE_PRODUCTS'] + "/legend/" + imgName
        # imgPath da cambiare - solo test
        imgPath = "/project/var/bars/new_data/" + imgName

        print("imgPath : " + imgPath)


        # basePath = "/home/ccmmma/prometeo/opt/ccmmmaapi/var/bars"
        basePath = "/project/var/bars"
        fileName = basePath + "/" + prod + "/bar_" + prod + "_" + output + "_" + position[0].lower() + ":" + lang + ".png"
        print("fileName : " + fileName)

        size = (width, height)

        if os.path.isfile(fileName):
            print("file exist")
            img = Image.open(fileName)
            img.thumbnail(size, Image.ANTIALIAS)
        else:
            print("file not exist")
            img = Image.new('RGBA', size)
            img.save(imgPath, 'PNG')

        with open(imgPath, 'rb') as content_file:
            data = content_file.read()

        return data

    def timeseries(self, params=None):
        retval = {}

        ms = MeteoServices(self.config)
        places = Places(self.config)
        prod = self.default_prod
        place = self.default_place

        timeref = None
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0

        if params:

            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

            if 'step' in params:
                step = int(params['step'])
            else:
                step = 1

            if 'hours' in params:
                hours = int(params['hours'])
            else:
                hours = 0

        if timeref is None:
            date = datetime.utcnow()
            year = date.year
            month = date.month
            day = date.day
            # hour=int(round(date.hour+date.minute/60.0))
            hour = 0
            minute = 0
        else:
            year = int(timeref[:4])
            month = int(timeref[4:6])
            day = int(timeref[6:8])
            hour = int(timeref[9:11])
            if len(timeref) == 13:
                minute = int(timeref[11:13])

        date = datetime(year, month, day, hour, minute)

        # Get the domain and the indeces of the place
        domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

        # Check if domain and indeces are correct
        if domain_indeces is not None:

            # Retrieve domain and indeces
            (domain, Jmin, Jmax, Imin, Imax) = domain_indeces

            retval = {"timeseries": []}

            done = False
            count = 0

            forecast = {}

            def do_stuff(q):
                while not q.empty():
                    item = q.get()
                    # print "Dequeued:"+str(item)
                    # print "Request:"+str(item)
                    # JSONDecodeError
                    try:
                        # text=requests.get(item).text
                        # print text
                        # data=simplejson.loads(text)
                        url = self.config['BASE_URL'] + "/products/" + item['prod'] + "/forecast/" + item[
                            'place'] + "?date=" + item['date'] + "&opt=" + params['opt']
                        data = requests.get(url).json()

                        # data=ms.modeloutput(item)

                        forecast[data['forecast']['dateTime']] = data['forecast']
                    except Exception as error_do_stuff:
                        print("error do_stuff()")
                        print("----------->" + str(error_do_stuff))

                    q.task_done()
                # print "Worker ended"

            items = []
            count = 0
            while count < 168:
                dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(
                    date.hour, '02') + format(date.minute, '02')
                dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

                url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config[
                    'HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"

                if os.path.isfile(url):
                    item = {"prod": prod, "place": place, "date": dateTime}
                    items.append(item)
                else:
                    break
                date = date + timedelta(hours=1)
                count = count + 1

            # print "Items:"+str(len(items))
            if self.config['NUM_THREADS'] > 1:
                q = Queue(maxsize=0)
                for item in items:
                    print("Queued:" + str(item))
                    q.put(item)

                # num_threads = items.count
                num_threads = items.__len__()
                if num_threads > self.config['NUM_THREADS']:
                    num_threads = self.config['NUM_THREADS']

                for i in range(num_threads):
                    worker = Thread(target=do_stuff, args=(q,))
                    worker.start()

                q.join()
            else:
                for item in items:
                    data = ms.modelOutput(item)
                    try:
                        forecast[data['forecast']['dateTime']] = data['forecast']
                    except Exception as e:
                        print("error for item in items")
                        print(str(e))

            keys = sorted(forecast)
            if hours == 0:
                hours = len(keys)
            # print len(keys),len(items)
            if len(keys) == len(items) or 1 == 1:
                autostep = 0
                if step < 1:
                    autostep = 1
                    step = self.products[prod]['autosteps'][autostep - 1]

                if step == 1 and autostep == 0:
                    hour = 0
                    for key in keys:
                        retval["timeseries"].append(forecast[key])
                        hour = hour + 1
                        if hour == hours:
                            break
                else:
                    count = 0
                    sums = {}
                    maxs = {}
                    mins = {}
                    iDate = None
                    dateTime = None
                    hour = 0
                    for key in keys:
                        if count == 0:
                            # initialize
                            dateTime = forecast[key]['dateTime']
                            if 'iDate' in forecast[key]:
                                iDate = forecast[key]['iDate']
                                # print "init:",dateTime
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("sum" in s for s in aggregateList) or any("ave" in s for s in aggregateList):
                                        sums[field] = forecast[key][field]

                                    if any("min" in s for s in aggregateList):
                                        mins[field] = forecast[key][field]

                                    if any("max" in s for s in aggregateList):
                                        maxs[field] = forecast[key][field]
                        else:
                            # store
                            # print "store:",key
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("sum" in s for s in aggregateList) or any("ave" in s for s in aggregateList):
                                        sums[field] = sums[field] + forecast[key][field]

                                    if any("max" in s for s in aggregateList):
                                        if forecast[key][field] > maxs[field]:
                                            maxs[field] = forecast[key][field]

                                    if any("min" in s for s in aggregateList):
                                        if forecast[key][field] < mins[field]:
                                            mins[field] = forecast[key][field]

                        count = count + 1
                        if count == step:
                            # print "aggr:",dateTime
                            # print str(sums)
                            # print str(mins)
                            # print str(maxs)
                            # aggregate
                            aggregated = {}
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("ave" in s for s in aggregateList):
                                        aggregated[field] = round(1.0 * sums[field] / count,
                                                                  self.products[prod]['fields'][field]['round'])

                                    if any("sum" in s for s in aggregateList):
                                        aggregated[field] = round(sums[field],
                                                                  self.products[prod]['fields'][field]['round'])

                                    if any("min" in s for s in aggregateList):
                                        aggregated[field + "-min"] = round(mins[field],
                                                                           self.products[prod]['fields'][field][
                                                                               'round'])

                                    if any("max" in s for s in aggregateList):
                                        aggregated[field + "-max"] = round(maxs[field],
                                                                           self.products[prod]['fields'][field][
                                                                               'round'])

                            aggregated["dateTime"] = dateTime
                            if iDate is not None:
                                aggregated["iDate"] = iDate
                            aggregated["link"] = "product=" + prod + "&place=" + place + "&date=" + dateTime
                            try:
                                aggregated['wchill'] = windChill(aggregated["t2c"], aggregated["ws10"])
                            except Exception:
                                pass

                            try:
                                aggregated['winds'] = windS(aggregated["wd10"])
                            except Exception:
                                pass

                            try:
                                current = {
                                    "date": dateTime,
                                    "crh": aggregated["crh"],
                                    "clf": aggregated["clf"]
                                }
                                aggregated['icon'], aggregated['text'] = iconText(current)
                                aggregated['icon'] = aggregated['icon'].replace("_night", "")
                                # print aggregated['icon']
                            except Exception:
                                # print str(e)
                                pass

                            # save
                            retval["timeseries"].append(aggregated)
                            if autostep > 0:
                                autostep = autostep + 1
                                step = self.products[prod]['autosteps'][autostep - 1]

                            count = 0

                # self.addDerivatedParams(retval['timeseries'])
                retval['result'] = "ok"
                if "opt" in params:
                    if "place" in params['opt']:
                        retval['place'] = places.get_place_by_id(place, params)
                    if "fields" in params['opt']:
                        retval['fields'] = self.products[prod]['fields']
            else:
                retval['result'] = "error"
                retval['details'] = "Data error"
        else:
            retval['result'] = "error"
            retval['details'] = "Place not indexed"

        return retval

    def getlegenddata1(self, prod, position, output, params=None):
        place = "ca004"
        data = None
        legendTheme = None

        width = self.default_xdim
        height = self.default_ydim

        timeref = None
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0

        if params:
            if 'width' in params and params['width'] is not None:
                width = int(params['width'])

            if 'height' in params and params['height'] is not None:
                height = int(params['height'])

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

        if timeref is None:
            # print "get current utc"
            date = datetime.utcnow()
            year = date.year
            month = date.month
            day = date.day
            hour = int(round(date.hour + date.minute / 60.0))
            minute = 0
        else:
            # print "Date is provided"
            year = int(timeref[:4])
            month = int(timeref[4:6])
            day = int(timeref[6:8])
            hour = int(timeref[9:11])
            if len(timeref) == 13:
                minute = int(timeref[11:13])

        # print "Place:"+str(place)
        date = datetime(year, month, day, hour, minute)
        # print "date:"+str(date)

        for theme in self.maps['themes'][prod][output]:
            for item in theme:
                if "LEGEND" in item and position in theme['LEGEND']:
                    legendTheme = theme
                    break
            if legendTheme is not None:
                break

        if legendTheme is not None:

            places = Places(self.config)

            # Get the domain and the indeces of the place
            domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

            # Check if domain and indeces are correct
            if domain_indeces is not None:

                # Retrieve domain and indeces
                (domain, Jmin, Jmax, Imin, Imax) = domain_indeces

                # Set the dateTime
                dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(
                    int(round(date.hour + date.minute / 60.0)), '02') + "00"
                dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

                url = self.config['WMS_URL'] + "/lds/opendap/" + prod + "/" + domain + "/" + self.config[
                    'HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc?"

                # url=url+'COLORBARONLY=true&'
                url = url + "LAYERS=" + theme['LAYERS'] + "&"

                url = url + 'COLORSCALERANGE=' + legendTheme['COLORSCALERANGE'] + "&"
                url = url + 'NUMCOLORBANDS=' + legendTheme['NUMCOLORBANDS'] + "&"
                url = url + 'ABOVEMAXCOLOR=' + legendTheme['ABOVEMAXCOLOR'] + "&"
                url = url + 'BELOWMINCOLOR=' + legendTheme['BELOWMINCOLOR'] + "&"
                url = url + 'BGCOLOR=' + legendTheme['BGCOLOR'] + "&"
                url = url + 'LOGSCALE=' + legendTheme['LOGSCALE'] + "&"
                url = url + 'STYLES=' + legendTheme['STYLES'] + "&"

                url = url + "FORMAT=image/png&"
                # url=url+"PALETTE=default&"

                if "top" in position or "bottom" in position:
                    url = url + "VERTICAL=false&"

                url = url + "SERVICE=WMS&VERSION=1.1.1&REQUEST=GetLegendGraphic&"
                url = url + "WIDTH=" + str(width) + "&HEIGHT=" + str(height)

                # print("-------------->"+str(url))

                try:
                    response = requests.get(url, stream=True)

                    if response.ok:
                        data = requests.get(url).content
                except:
                    pass

        if data is None:
            # Generate a bitmap
            imgName = "legend_" + prod + "_" + position + "_" + output + "_" + str(width) + "x" + str(height) + ".png"
            imgPath = self.config['BASE_PRODUCTS'] + "/legend/" + imgName
            img = Image.new('RGBA', (width, height))
            img.save(imgPath, 'PNG')
            with open(imgPath, 'r') as content_file:
                data = content_file.read()

        return data

    def timeseries(self, params=None):
        retval = {}

        ms = MeteoServices(self.config)
        places = Places(self.config)
        prod = self.default_prod
        place = self.default_place

        timeref = None
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0

        if params:

            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']

            if 'place' in params and params['place'] is not None:
                place = params['place']

            if 'date' in params and params['date'] is not None:
                timeref = params['date']

            if 'step' in params:
                step = int(params['step'])
            else:
                step = 1

            if 'hours' in params:
                hours = int(params['hours'])
            else:
                hours = 0

        if timeref is None:
            date = datetime.utcnow()
            year = date.year
            month = date.month
            day = date.day
            # hour=int(round(date.hour+date.minute/60.0))
            hour = 0
            minute = 0
        else:
            year = int(timeref[:4])
            month = int(timeref[4:6])
            day = int(timeref[6:8])
            hour = int(timeref[9:11])
            if len(timeref) == 13:
                minute = int(timeref[11:13])

        date = datetime(year, month, day, hour, minute)

        # Get the domain and the indeces of the place
        domain_indeces = places.get_domain_and_indeces_by_product_and_place(prod, place)

        # Check if domain and indeces are correct
        if domain_indeces is not None:

            # Retrieve domain and indeces
            (domain, Jmin, Jmax, Imin, Imax) = domain_indeces

            retval = {"timeseries": []}

            done = False
            count = 0

            forecast = {}

            def do_stuff(q):
                while not q.empty():
                    item = q.get()
                    # print "Dequeued:"+str(item)
                    # print "Request:"+str(item)
                    # JSONDecodeError
                    try:
                        # text=requests.get(item).text
                        # print text
                        # data=simplejson.loads(text)
                        url = self.config['BASE_URL'] + "/products/" + item['prod'] + "/forecast/" + item[
                            'place'] + "?date=" + item['date'] + "&opt=" + params['opt']
                        data = requests.get(url).json()

                        # data=ms.modeloutput(item)

                        forecast[data['forecast']['dateTime']] = data['forecast']
                    except Exception as e:
                        print("----------->" + str(e))

                    q.task_done()
                # print "Worker ended"

            items = []
            count = 0
            while count < 168:
                dateTime = format(date.year, '04') + format(date.month, '02') + format(date.day, '02') + "Z" + format(
                    date.hour, '02') + format(date.minute, '02')
                dateTimePath = format(date.year, '04') + "/" + format(date.month, '02') + "/" + format(date.day, '02')

                url = self.config['BASE_PATH'] + "/" + prod + "/" + domain + "/" + self.config[
                    'HISTORY'] + "/" + dateTimePath + "/" + prod + "_" + domain + "_" + dateTime + ".nc"

                if os.path.isfile(url):
                    item = {"prod": prod, "place": place, "date": dateTime}
                    items.append(item)
                else:
                    break
                date = date + timedelta(hours=1)
                count = count + 1

            # print "Items:"+str(len(items))
            if self.config['NUM_THREADS'] > 1:
                q = Queue(maxsize=0)
                for item in items:
                    # print("Queued:" + str(item))
                    q.put(item)

                # num_threads = items.count
                num_threads = items.__len__()
                if num_threads > self.config['NUM_THREADS']:
                    num_threads = self.config['NUM_THREADS']

                for i in range(num_threads):
                    worker = Thread(target=do_stuff, args=(q,))
                    worker.start()

                q.join()
            else:
                for item in items:
                    data = ms.modelOutput(item)
                    try:
                        forecast[data['forecast']['dateTime']] = data['forecast']
                    except Exception as e:
                        print(str(e))

            keys = sorted(forecast)
            if hours == 0:
                hours = len(keys)
            # print len(keys),len(items)
            if len(keys) == len(items) or 1 == 1:
                autostep = 0
                if step < 1:
                    autostep = 1
                    step = self.products[prod]['autosteps'][autostep - 1]

                if step == 1 and autostep == 0:
                    hour = 0
                    for key in keys:
                        retval["timeseries"].append(forecast[key])
                        hour = hour + 1
                        if hour == hours:
                            break
                else:
                    count = 0
                    sums = {}
                    maxs = {}
                    mins = {}
                    iDate = None
                    dateTime = None
                    hour = 0
                    for key in keys:
                        if count == 0:
                            # initialize
                            dateTime = forecast[key]['dateTime']
                            if 'iDate' in forecast[key]:
                                iDate = forecast[key]['iDate']
                                # print "init:",dateTime
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("sum" in s for s in aggregateList) or any("ave" in s for s in aggregateList):
                                        sums[field] = forecast[key][field]

                                    if any("min" in s for s in aggregateList):
                                        mins[field] = forecast[key][field]

                                    if any("max" in s for s in aggregateList):
                                        maxs[field] = forecast[key][field]
                        else:
                            # store
                            # print "store:",key
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("sum" in s for s in aggregateList) or any("ave" in s for s in aggregateList):
                                        sums[field] = sums[field] + forecast[key][field]

                                    if any("max" in s for s in aggregateList):
                                        if forecast[key][field] > maxs[field]:
                                            maxs[field] = forecast[key][field]

                                    if any("min" in s for s in aggregateList):
                                        if forecast[key][field] < mins[field]:
                                            mins[field] = forecast[key][field]

                        count = count + 1
                        if count == step:
                            # print "aggr:",dateTime
                            # print str(sums)
                            # print str(mins)
                            # print str(maxs)
                            # aggregate
                            aggregated = {}
                            for field in forecast[key]:
                                if 'aggregate' in self.products[prod]['fields'][field]:
                                    aggregateList = self.products[prod]['fields'][field]['aggregate']
                                    if any("ave" in s for s in aggregateList):
                                        aggregated[field] = round(1.0 * sums[field] / count,
                                                                  self.products[prod]['fields'][field]['round'])

                                    if any("sum" in s for s in aggregateList):
                                        aggregated[field] = round(sums[field],
                                                                  self.products[prod]['fields'][field]['round'])

                                    if any("min" in s for s in aggregateList):
                                        aggregated[field + "-min"] = round(mins[field],
                                                                           self.products[prod]['fields'][field][
                                                                               'round'])

                                    if any("max" in s for s in aggregateList):
                                        aggregated[field + "-max"] = round(maxs[field],
                                                                           self.products[prod]['fields'][field][
                                                                               'round'])

                            aggregated["dateTime"] = dateTime
                            if iDate is not None:
                                aggregated["iDate"] = iDate
                            aggregated["link"] = "product=" + prod + "&place=" + place + "&date=" + dateTime
                            try:
                                aggregated['wchill'] = windChill(aggregated["t2c"], aggregated["ws10"])
                            except Exception as e:
                                pass

                            try:
                                aggregated['winds'] = windS(aggregated["wd10"])
                            except Exception as e:
                                pass

                            try:
                                current = {
                                    "date": dateTime,
                                    "crh": aggregated["crh"],
                                    "clf": aggregated["clf"]
                                }
                                aggregated['icon'], aggregated['text'] = iconText(current)
                                aggregated['icon'] = aggregated['icon'].replace("_night", "")
                                # print aggregated['icon']
                            except Exception as e:
                                # print str(e)
                                pass

                            # save
                            retval["timeseries"].append(aggregated)
                            if autostep > 0:
                                autostep = autostep + 1
                                step = self.products[prod]['autosteps'][autostep - 1]

                            count = 0

                # self.addDerivatedParams(retval['timeseries'])
                retval['result'] = "ok"
                if "opt" in params:
                    if "place" in params['opt']:
                        retval['place'] = places.get_place_by_id(place, params)
                    if "fields" in params['opt']:
                        retval['fields'] = self.products[prod]['fields']
            else:
                retval['result'] = "error"
                retval['details'] = "Data error"
        else:
            retval['result'] = "error"
            retval['details'] = "Place not indexed"

        return retval

    def modelcharturl(self, params=None):
        # log.info("modelcharturl")
        # url = self.base_url + 'charts.php'
        url = self.config['BASE_URL'] + 'charts.php'
        print(url)
        prod = self.default_prod
        place = self.default_place
        output = 'tsp'
        hours = 144
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        step = 1
        md5 = ""
        hour = '00'

        if params:
            if 'prod' in params and params['prod'] is not None:
                prod = params['prod']
            if 'place' in params and params['place'] is not None:
                place = params['place']
            if 'step' in params and params['step'] is not None:
                step = params['step']
            if 'hours' in params and params['hours'] is not None:
                hours = params['hours']
            if 'output' in params and params['output'] is not None:
                output = params['output']
            if 'md5' in params and params['md5'] is not None:
                md5 = params['md5']

        date = str(year) + str(month) + str(day) + 'Z' + hour

        fields = {
            'dry': 'true',
            'prod': urllib.quote_plus(prod),
            'place': urllib.quote_plus(place),
            'output': urllib.quote_plus(output),
            'date': urllib.quote_plus(date),
            'step': urllib.quote_plus(str(step)),
            'hours': urllib.quote_plus(str(hours)),
            'md5': urllib.quote_plus(str(md5))
        }

        full_link = self.__getFullLink(url, fields)
        if "DEBUG" in os.environ:
            print("full_link:%s" % full_link)

        data = self.__executeRequest(full_link)
        # log.info("full_link: " + str(full_link))
        # log.info("data     : " + str(data))
        if not data:
            return self.__statusCode['404']
        try:
            result = xmltodict.parse(data)
        except:
            return self.__statusCode['400']
        return result
