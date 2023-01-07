# flask용 모듈
from flask import Flask, request, jsonify
# crawling용 모듈
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import urllib
import json
import datetime

import sys

class Weather:
    def weath(req):
        
        headers = {"User_Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/573.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
                  "Connection": "close"}
        
        params = req['action']['detailParams']  # 사용자가 전송한 실제 메시지

        strN = []
        answer = ""
        location = ""

        if 'sys_location1' in params.keys(): # 지역을 시 구 동으로 3개까지 입력을 받을 수 있어서 순서대로 location에 저장
            location = params['sys_location1']['value']
        if 'sys_location2' in params.keys():
            location += "+" + params['sys_location2']['value']
        if 'sys_location3' in params.keys():
            location += "+" + params['sys_location3']['value']
        
        url = 'https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=' + location + "+날씨"
        html = requests.get(url, headers=headers)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, 'lxml')
        
        if 'this_week' in params.keys():
            week_date = ["월", "화", "수", "목", "금", "토", "일"]
            week_idx = datetime.datetime.today().weekday()
            _today = week_date[week_idx]
            _tomorrow = 0
            if week_idx == 6:
                _tomorrow = week_date[0]
            else:
                _tomorrow = week_date[week_idx+1]

            weather_week = soup.find('ul', {'class': 'week_list'}).find_all('li', {'class': 'week_item'})
            weeks = []
            for week in weather_week:
                weeks.append(week.text.strip().replace("      ", " ").replace("    ", " ").replace("     ", " ").replace("  ", " ")
                .replace(" 오전", "").replace(" 오후", "").replace("최저기온", "").replace("최고기온", "").replace("오늘", f"{_today}")
                .replace("내일", f"{_tomorrow}").replace("흐리고 비", "흐리고비").replace("흐리고 한때 비/눈", "흐리고비")
                .replace("구름많고 한때 비/눈", "흐리고비").replace("흐리고 한때 눈", "흐리고비").replace("흐리고 한때 비", "흐리고비")
                .replace("구름많고 한때 눈", "흐리고비").replace("구름많고 한때 비", "흐리고비")
                .replace("흐리고 가끔 비/눈", "흐리고비").replace("흐리고 가끔 눈", "흐리고비").replace("흐리고 가끔 비", "흐리고비")
                .replace("구름많고 가끔 비/눈", "흐리고비").replace("구름많고 가끔 눈", "흐리고비").replace("구름많고 가끔 비", "흐리고비")
                .replace("맑고 한때 비/눈", "흐리고비").replace("맑고 한때 눈", "흐리고비").replace("맑고 한때 비", "흐리고비")
                .replace("맑고 가끔 비/눈", "흐리고비").replace("맑고 가끔 눈", "흐리고비").replace("맑고 가끔 비", "흐리고비")
                .replace("흐리고 눈", "흐리고눈").replace("구름많고 눈", "구름많눈"))
            #print(weeks)

            idx1 = {"0": 7, "1": 6, "2": 5, "3": 4, "4": 3, "5": 2, "6": 1}.get(str(week_idx), 0)
            
            strN.append("   날짜      강수확률(기상)    온도\n")  
            for i in range(idx1):
                week = []
                week.append(weeks[i].split())
                if idx1-1 == i:
                    if week[0][2] == '0%':
                        strN.append(f"{week[0][0]} {week[0][1]}     {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}")
                    else:
                    	strN.append(f"{week[0][0]} {week[0][1]}    {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}")
                else:
                    if week[0][2] == '0%':
                        strN.append(f"{week[0][0]} {week[0][1]}     {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}\n")
                    else:
                    	strN.append(f"{week[0][0]} {week[0][1]}    {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}\n")
                    
        elif 'week_next' in params.keys():
            week_date = ["월", "화", "수", "목", "금", "토", "일"]
            week_idx = datetime.datetime.today().weekday()
            _today = week_date[week_idx]
            _tomorrow = 0
            if week_idx == 6:
                tomorrow = week_date[0]
            else:
                tomorrow = week_date[week_idx+1]

            weather_week = soup.find('ul', {'class': 'week_list'}).find_all('li', {'class': 'week_item'})
            weeks = []
            for week in weather_week:
                weeks.append(week.text.strip().replace("      ", " ").replace("    ", " ").replace("     ", " ").replace("  ", " ")
                .replace(" 오전", "").replace(" 오후", "").replace("최저기온", "").replace("최고기온", "").replace("오늘", f"{_today}")
                .replace("내일", f"{_tomorrow}").replace("흐리고 비", "흐리고비").replace("흐리고 한때 비/눈", "흐리고비")
                .replace("구름많고 한때 비/눈", "흐리고비").replace("흐리고 한때 눈", "흐리고비").replace("흐리고 한때 비", "흐리고비")
                .replace("구름많고 한때 눈", "흐리고비").replace("구름많고 한때 비", "흐리고비")
                .replace("흐리고 가끔 비/눈", "흐리고비").replace("흐리고 가끔 눈", "흐리고비").replace("흐리고 가끔 비", "흐리고비")
                .replace("구름많고 가끔 비/눈", "흐리고비").replace("구름많고 가끔 눈", "흐리고비").replace("구름많고 가끔 비", "흐리고비")
                .replace("맑고 한때 비/눈", "흐리고비").replace("맑고 한때 눈", "흐리고비").replace("맑고 한때 비", "흐리고비")
                .replace("맑고 가끔 비/눈", "흐리고비").replace("맑고 가끔 눈", "흐리고비").replace("맑고 가끔 비", "흐리고비")
                .replace("흐리고 눈", "흐리고눈").replace("구름많고 눈", "구름많눈"))

                
            idx1 = {"0": 7, "1": 6, "2": 5, "3": 4, "4": 3, "5": 2, "6": 1}.get(str(week_idx), 0)
            idx2 = {"1": 8, "2": 9}.get(str(idx1), 10)

            strN.append("   날짜     강수확률(기상)    온도\n")  
            for i in range(idx1, idx2):
                week = []
                week.append(weeks[i].split())
                if idx2-1 == i:
                    if week[0][2] == '0%':
                        strN.append(f"{week[0][0]} {week[0][1]}     {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}")
                    else:
                    	strN.append(f"{week[0][0]} {week[0][1]}    {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}")
                else:
                    if week[0][2] == '0%':
                        strN.append(f"{week[0][0]} {week[0][1]}     {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}\n")
                    else:
                    	strN.append(f"{week[0][0]} {week[0][1]}    {week[0][2]:>3} / {week[0][4]:>3}   {week[0][6]:>4}/{week[0][8]:>4}\n")

        elif 'tomorrow' in params.keys():
            tomorrow_temp = soup.find('ul', {'class': 'weather_info_list _tomorrow'})
            
            am = tomorrow_temp.find('div', {'class': '_am'})
            tem_text_am = am.find('div', {'class': 'temperature_text'}).text.strip()[5:]
            tem_info_am1 = am.find('p', {'class': 'summary'}).text
            tem_info_am2 = am.find('dd', {'class': 'desc'}).text
            
            pm = tomorrow_temp.find('div', {'class': '_pm'})
            tem_text_pm = pm.find('div', {'class': 'temperature_text'}).text.strip()[5:]
            tem_info_pm1 = pm.find('p', {'class': 'summary'}).text
            tem_info_pm2 = pm.find('dd', {'class': 'desc'}).text
            
            air = tomorrow_temp.find('ul', {'class': 'today_chart_list'})
            air_all = air.find_all('li', {'class': 'item_today'})
            
            strN.append(location.replace("+", " ") + " 내일 기상정보입니다.\n")
            strN.append(f"온도: {tem_text_am} ~ {tem_text_pm}\n")
            strN.append(f"하늘: {tem_info_am1} ~ {tem_info_pm1}\n")
            strN.append(f"강수확률: {tem_info_am2} ~ {tem_info_pm2}\n")
            strN.append(f"{air_all[0].text.strip()} 입니다.\n")
            strN.append(f"{air_all[1].text.strip()} 입니다.")    
            
        elif 'after_tomorrow' in params.keys():
            after_tomorrow_temp = soup.find('ul', {'class': 'weather_info_list _after_tomorrow'})
            
            am = after_tomorrow_temp.find('div', {'class': '_am'})
            tem_text_am = am.find('div', {'class': 'temperature_text'}).text.strip()[5:]
            tem_info_am1 = am.find('p', {'class': 'summary'}).text
            tem_info_am2 = am.find('dd', {'class': 'desc'}).text
            
            pm = after_tomorrow_temp.find('div', {'class': '_pm'})
            tem_text_pm = pm.find('div', {'class': 'temperature_text'}).text.strip()[5:]
            tem_info_pm1 = pm.find('p', {'class': 'summary'}).text
            tem_info_pm2 = pm.find('dd', {'class': 'desc'}).text
            
            air = after_tomorrow_temp.find('ul', {'class': 'today_chart_list'})
            air_all = air.find_all('li', {'class': 'item_today'})
            
            strN.append(location.replace("+", " ") + " 모레 기상정보입니다.\n")
            strN.append(f"온도: {tem_text_am} ~ {tem_text_pm}\n")
            strN.append(f"하늘: {tem_info_am1} ~ {tem_info_pm1}\n")
            strN.append(f"강수확률: {tem_info_am2} ~ {tem_info_pm2}\n")
            strN.append(f"{air_all[0].text.strip()} 입니다.\n")
            strN.append(f"{air_all[1].text.strip()} 입니다.")    
            
        elif 'sys_date' not in params.keys() or 'sys_date' in params.keys():
            weather_data = soup.find('div', {'class': 'weather_info'})

                # 현재 온도
            temperature = weather_data.find('div', {'class': 'temperature_text'}).text.strip()[5:]

                # 날씨 상태 
            weather_status = soup.find('p', {'class': 'summary'})
            weather_status1 = weather_status.find('span', {'class': 'temperature'}).text
            weather_status2 = weather_status.find('span', {'class': 'weather before_slash'}).text

                # 공기 상태
            air = soup.find('ul', {'class': 'today_chart_list'})
            air_all = air.find_all('li', {'class': 'item_today'})

            strN.append(location.replace("+", " ") + " 현재 기상정보입니다.\n")
            strN.append(f"현재 온도: {temperature}\n")
            strN.append(f"어제보다 {weather_status1}\n")
            strN.append(f"하늘 상태는 {weather_status2} 입니다.\n")
            strN.append(f"{air_all[0].text.strip()} 입니다.\n")
            strN.append(f"{air_all[1].text.strip()} 입니다.")
    	
        answer = ''.join(strN)
        strN = []
        return answer