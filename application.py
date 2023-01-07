# flask용 모듈
from flask import Flask, request, jsonify
# crawling용 모듈
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import urllib
import json, datetime
# from multiprocessing import pool

import sys


from weather import Weather
from sports_baseball import Sports
from stock import Stock


application = Flask(__name__)


@application.route("/")
def hello():
    return "Hello goorm!"


@application.route("/weather",methods=['POST'])
def weather():
    req = request.get_json()
    answer = Weather.weath(req)
    res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }

    return jsonify(res)
    


@application.route("/sports",methods=['POST'])
def sports():
    req = request.get_json()
    answer = Sports()
    text = answer.sport(req)
    res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": text
                        }
                    }
                ]
            }
        }

    return jsonify(res)

@application.route("/stock",methods=['POST'])
def stock():
    req = request.get_json()
    answer = Stock.stocks(req)
    
    res = {
        "version": "2.0",
        "template": {
    		"outputs": [
            	{
                	"simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    
    return jsonify(res)


    return jsonify(res)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, debug = True, threaded=True)
    
