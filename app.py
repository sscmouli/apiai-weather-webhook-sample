#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    #res = processRequest(req)
    result = req.get("result")
    parameters = result.get("parameters")
    zip_code = parameters.get("zip-code")
    movie = parameters.get("movie")

    given_time = parameters.get("times")

    if given_time is None:
        given_time = ""
    not_possible_times = []

    given_time = given_time.split(",")[1:]

    print(given_time)

    for poss_time in given_time:
        not_possible_times.append(poss_time[:-3])

    print(not_possible_times)
    print(movie)
    print(zip_code)


    print("aks1")

    baseurl = "http://data.tmsapi.com/v1.1/movies/showings?startDate=2017-02-05&numDays=1&zip="+zip_code+"&api_key=ebevjaxjs52b6dfuep2pke6d"
    result = urllib.request.urlopen(baseurl).read()
    data = json.loads(result)

    print("aks2")
    #print(data[0])
    #print(data)

    #theaters = ["AMC Mercado 20", "Century Cinema 16"]
    showtimes = {}

    print("aks2.5")
    #print(data[0]['title'])
    for movie_item in data:
        print(movie_item['title'])
        print(movie)
        print(movie in movie_item['title'])
        if movie in movie_item['title']:
            showtimes_theater = movie_item['showtimes']
            print(movie_item['showtimes'][0])
            for stt in showtimes_theater:
                if stt['theatre']['name'] not in showtimes:
                    showtimes[stt['theatre']['name']] = []
                print(stt['theatre']['name'])
                time_show = stt['dateTime'][11:]
                if time_show not in not_possible_times:
                    showtimes[stt['theatre']['name']].append(time_show)
    print("aks3")
    print(showtimes)

    speech = ""

    for showtime in showtimes:
        speech = speech + "Showtimes in " + showtime + " " + " ".join(showtimes[showtime]) + "\n"

        print(speech)
    #showtimes = json.dumps(showtimes)
    
    res = {
        "speech": speech,
        "displayText": speech,
        "source": "data.tmsapi.com"
    }

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.request.urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
