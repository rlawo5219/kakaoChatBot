# flask용 모듈
from flask import Flask, request, jsonify
# crawling용 모듈
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import urllib
import json
import sys


class Stock:
    def stocks(req):
        params = req['action']['detailParams']
        index = ""
        answer = ""
        a = []
        
        #기업 주가 확인
        if 'sys_kospi' in params.keys():
            index = params['sys_kospi']['value']
            
            url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query='+index
            rea = requests.get(url)
            rea.raise_for_status()
            soup = BeautifulSoup(rea.text,'lxml')
            code = soup.find('div',{'class':'spt_tlt'})
            codes= code.find('span',{'class': 'spt_con'}).text
            a = codes.split()
            answer += f"{index} 주가\n{a[0]}{a[1]}\n{a[2]}{a[3]}{a[5]}\n{a[6]}"
            
    	
        #코스피 지수 확인 #1번 방법
        elif 'sys_piindex' in params.keys():
            index = params['sys_piindex']['value']
            
            url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=코스피'
            rea = requests.get(url)
            rea.raise_for_status()
            soup = BeautifulSoup(rea.text,'lxml')
            code = soup.find('div',{'class':'spt_tlt'})
            codes = code.find('span', {'class': 'spt_con'}).text
            a = codes.split()
            answer += f"{index} 지수\n{a[0]}{a[1]}\n{a[2]}{a[3]}\n{a[4]}"

        #코스닥 지수 확인 #2번 방법
        elif 'sys_daqindex' in params.keys():
            index = params['sys_daqindex']['value']
            
            url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=코스닥'
            rea = requests.get(url)
            rea.raise_for_status()
            soup = BeautifulSoup(rea.text,'lxml')
            code = soup.find('div',{'class':'spt_tlt'})
            codes = code.find('span', {'class': 'spt_con'}).text
            a = codes.split()
            answer += f"{index} 지수\n{a[0]}{a[1]}\n{a[2]}{a[3]}\n{a[4]}"

        #환율 확인
        elif 'sys_nation' in params.keys():
            index = params['sys_nation']['value']
            
            url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='+index+"환율"
            rea = requests.get(url)
            rea.raise_for_status()
            soup = BeautifulSoup(rea.text,'lxml')
            code = soup.find('div',{'class':'rate_tlt'})
            codes = code.find('span', {'class': 'spt_con'}).text
            a = codes.split()
            answer += f"{index} 환율\n{a[0]}\n{a[1]}\n{a[2]}"
            
        
        return answer
    	