# flask용 모듈
from flask import Flask, request, jsonify
import json
import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import datetime as dt
from datetime import timedelta


# 국내 야구 일정

class Sports:
    day = dt.date.today().day
    month = dt.datetime.now().month
    week_idx = dt.date.today().weekday()
    
    def baseballScheduleCrawling(self):
        dataList = []

        months = [self.month]
        if (self.day <= 14):
            months = [self.month - 1, self.month]
        elif(self.day >= 17):
            months = [self.month,self.month+1]

        for month in months:
            url = f"https://sports.news.naver.com/kbaseball/schedule/index?date=20220929&month={month}&year=2022&teamCode="
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력
            soup = BeautifulSoup(res.text, "lxml")

            soupData = [soup.findAll("div", {"class": "sch_tb"}),
                        soup.findAll("div", {"class": "sch_tb2"})]  # sch_tb 짝수날짜, sch_tb2 홀수날짜

            for dataTb in soupData:
                for data in dataTb:
                    # 모든 날짜
                    dateValue = data.find("span", {"class": "td_date"}).text
                    # input을 위한 날짜 정규화
                    dateValue2 = data.find("strong").text
                    dateValue2 = dateValue2.split(".")
                    # print(dateValue2)
                    if (int(dateValue2[0]) < 10):
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-0{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-0{dateValue2[0]}-{dateValue2[1]}"
                    else:
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-{dateValue2[0]}-{dateValue2[1]}"

                    if (len(dateValue.split(" ")[0].split(".")[1]) == 1):
                        # 날짜 정규화
                        dateValue = dateValue.split(" ")[0].split(".")[0] + ".0" + dateValue.split(" ")[0].split(".")[
                            1] + " " + \
                                    dateValue.split(" ")[1]
                    matchNum = data.find("td")["rowspan"]
                    for i in range(int(matchNum)):
                        matchData = {}  # 모든 경기 정보 저장하는 딕셔너리
                        # 날짜
                        matchData["date"] = dateValue
                        matchData["dateForSearch"] = dateValue2
                        # 시간
                        matchData["time"] = data.findAll("tr")[i].find("span", {"class": "td_hour"}).text
                        # 경기 없을 시 matchData["time"] = "-"
                        if matchData["time"] != "-":  # 경기 일정이 있을때
                            # 홈팀
                            matchData["home"] = data.findAll("tr")[i].find("span", {"class": "team_rgt"}).text
                            # 어웨이팀
                            matchData["away"] = data.findAll("tr")[i].find("span", {"class": "team_lft"}).text
                            # VS일 시 진행예정경기
                            if data.findAll("tr")[i].find("strong", {"class": "td_score"}).text != "VS":  # 종료된 경기일 때
                                # 홈팀 스코어
                                matchData["homeScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[1]
                                # 어웨이팀 스코어
                                matchData["awayScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[0]
                            else:  # 진행 예정 경기일 떄
                                matchData["homeScore"] = "-"
                                matchData["awayScore"] = "-"
                            # 경기장
                            matchData["stadium"] = data.findAll("tr")[i].findAll("span", {"class": "td_stadium"})[
                                1].text
                            # 중계방송사
                            matchData["platform"] = data.findAll("tr")[i].findAll("span", {"class": "td_stadium"})[
                                0].text.strip()
                        else:  # 경기 일정이 없을 시
                            matchData["home"] = "-"
                            matchData["away"] = "-"
                            matchData["homeScore"] = "-"
                            matchData["awayScore"] = "-"
                            matchData["stadium"] = "-"
                            matchData["platform"] = "-"
                        dataList.append(matchData)
        return dataList

    # 일정 조회 함수
    def baseballSchedule(self, search):
        ans = ""
        offSeason = [1, 2, 12]

        # 오프시즌일 때
        if search.month in offSeason:
            ans += f"{search}일은 시즌 중의 날짜가 아닙니다.\n"
            return ans
        dataList = self.baseballScheduleCrawling()
        search = search.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == search):
                # 경기일정이 있을 때
                if (data.get('time') != '-'):
                    # 끝나거나, 진행 중인 경기일 때
                    if (data.get('homeScore') != '-'):
                        # 홈 팀이 이겼을 떄
                        if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                        # 원정 팀이 이겼을 때
                        if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                    # 경기가 취소됐을 때
                    elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                        ans += f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                    # 진행 예정인 경기일 때
                    else:
                        ans += f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정이며, {data.get('platform')}을 통해서 중계됩니다.\n"

                # 경기 일정이 없을 때
                else:
                    ans += f"{data.get('date')}요일 경기 일정은 없습니다.\n"
        return ans

    def baseballTeamSchedule(self,date, teamname):
        ans = ""
        offSeason = [1,2,12]
        if date.month in offSeason:
            ans += f"{date}일은 시즌 중의 날짜가 아닙니다\n"
            return ans
        dataList = self.baseballScheduleCrawling()
        date = date.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == date):
                if (data["home"] == teamname or data["away"] == teamname):
                    # 경기일정이 있을 때
                    if (data.get('time') != '-'):
                        # 끝나거나, 진행 중인 경기일 때
                        if (data.get('homeScore') != '-'):
                            # 홈 팀이 이겼을 떄
                            if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                            # 원정 팀이 이겼을 때
                            if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                        # 경기가 취소됐을 때
                        elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                            ans = f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                        # 진행 예정인 경기일 때
                        else:
                            ans = f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정이며, {data.get('platform')}을 통해서 중계됩니다.\n"

            if (ans == ""):
                ans = f"{date}일의 {teamname}팀의 일정은 없습니다\n"
        return ans    

    def baseballTeamdataCrawling(self):
        ans = ""
        url = f"https://sports.news.naver.com/kbaseball/record/index?category=kbo"
        res = requests.get(url)
        res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

        soup = BeautifulSoup(res.text, "lxml")
        soupData = soup.find("tbody", {"id": "regularTeamRecordList_table"})
        dataList = []  # 모든 순위정보 저장 리스트
        for data in soupData.findAll("tr"):
            ans = ""
            teamData = {}  # 순위 정보 저장 딕셔너리
            # 팀 순위
            teamData["rank"] = data.findAll('strong')[0].text
            # 팀 이름
            teamData["team"] = data.findAll("span")[1].text
            # 경기수
            teamData["total"] = data.findAll("span")[2].text
            # 승리수
            teamData["win"] = data.findAll("span")[3].text
            # 패배수
            teamData["lose"] = data.findAll("span")[4].text
            # 무승부 수
            teamData["draw"] = data.findAll("span")[5].text
            # 승률
            teamData["winRate"] = data.findAll('strong')[1].text
            # 게임차
            teamData["difference"] = data.findAll("span")[6].text
            # 연속
            teamData["streak"] = data.findAll("span")[7].text
            # 출루율
            teamData["onBasePer"] = data.findAll("span")[8].text
            # 장타율
            teamData["slugPer"] = data.findAll("span")[9].text
            # 최근 10경기
            teamData["lastTenMatches"] = data.findAll("span")[10].text
            dataList.append(teamData)
        return dataList

    def baseballTeamData(self, team):
        dataList = self.baseballTeamdataCrawling()
        ans = ""
        for data in dataList:
            if (data["team"].replace(" ", "") == team.replace(" ", "")):
                ans = f"{data.get('team')}의 순위는 {data.get('rank')}위입니다.\n" \
                      f"현재 {data.get('total')}전 {data.get('win')}승 {data.get('lose')}패 {data.get('draw')}무를 기록 중으로 " \
                      f"승률은 {float(data.get('winRate')) * 100}%\n 1위와 {data.get('difference')} 게임차입니다.\n" \
                      f"출루율은 {data.get('onBasePer')}, 장타율은 {data.get('slugPer')}입니다.\n" \
                      f"최근 10게임 전적은 {data.get('lastTenMatches')}입니다."
                break
            else:
                ans = "해당 팀은 존재하지 않습니다."
        return ans

    def baseballRanking(self):
        dataList = self.baseballTeamdataCrawling()
        ans = "순위 \t팀\t   경기  \t승   \t패  \t무 \t게임차\n\n"
        for data in dataList:
            ans += f" {data.get('rank')}    \t{data.get('team')}  \t{data.get('total')}  \t" \
                   f"{data.get('win')}  \t{data.get('lose')}  \t{data.get('draw')} \t{data.get('difference')}\n"
        return ans

    def basketballScheduleCrawling(self):
        dataList = []
        offSeason = [6, 7, 8, 9]

        months = [self.month]
        if (self.day <= 14):
            months = [self.month - 1, self.month]
        elif(self.day >= 17):
            months = [self.month,self.month+1]
            
        for month in months:
            url = f"https://sports.news.naver.com/basketball/schedule/index?date=20221001&month={month}&year=2022&teamCode=&category=kbl"
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

            soup = BeautifulSoup(res.text, "lxml")
            soupData = [soup.findAll("div", {"class": "sch_tb"}), soup.findAll("div", {"class": "sch_tb2"})]  # 짝수, 홀수
            for dataTb in soupData:
                for data in dataTb:
                    # 모든 날짜
                    dateValue = data.find("span", {"class": "td_date"}).text

                    # input을 위한 날짜 정규화
                    dateValue2 = data.find("strong").text
                    dateValue2 = dateValue2.split(".")
                    if (int(dateValue2[0]) < 10):
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-0{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-0{dateValue2[0]}-{dateValue2[1]}"
                    else:
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-{dateValue2[0]}-{dateValue2[1]}"

                    if (len(dateValue.split(" ")[0].split(".")[1]) == 1):
                        dateValue = dateValue.split(" ")[0].split(".")[0] + ".0" + dateValue.split(" ")[0].split(".")[
                            1] + " " + dateValue.split(" ")[1]

                    matchNum = data.find("td")["rowspan"]  # 경기가 없는 날의 rowspan == 5, 있는 날의 rowspan은 경기수
                    if (int(matchNum) == 5):
                        matchNum = '1'
                    for i in range(int(matchNum)):
                        matchData = {}  # 모든 경기정보 저장하는 딕셔너리
                        # 날짜
                        matchData["date"] = dateValue
                        matchData["dateForSearch"] = dateValue2
                        # 시간
                        matchData["time"] = data.findAll("tr")[i].find("span", {"class": "td_hour"}).text
                        if matchData["time"] != "-":  # 경기 일정이 있을때
                            # 홈팀
                            matchData["home"] = data.findAll("tr")[i].find("span", {"class": "team_lft"}).text
                            # 어웨이팀
                            matchData["away"] = data.findAll("tr")[i].find("span", {"class": "team_rgt"}).text
                            # VS일 시 무승부나 진행예정경기
                            if data.findAll("tr")[i].find("strong", {"class": "td_score"}).text != "VS":  # 종료된 경기일 때
                                # 홈팀 스코어
                                matchData["homeScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[0]
                                # 어웨이팀 스코어
                                matchData["awayScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[1]
                            else:  # 진행 예정 경기일 떄
                                matchData["homeScore"] = "-"
                                matchData["awayScore"] = "-"
                            # 경기장
                            matchData["stadium"] = data.findAll("tr")[i].findAll("span", {"class": "td_stadium"})[
                                0].text
                        else:  # 경기 일정이 없을 시
                            matchData["home"] = "-"
                            matchData["away"] = "-"
                            matchData["homeScore"] = "-"
                            matchData["awayScore"] = "-"
                            matchData["stadium"] = "-"
                        dataList.append(matchData)
        return dataList

    def basketballSchedule(self, search):
        ans = ""
        offSeason = [6, 7, 8, 9]
        # 오프시즌일 때
        if search.month in offSeason:
            ans += f"{search}일은 시즌 중의 날짜가 아닙니다.\n"
            return ans
        search = search.strftime("%Y-%m-%d")
        dataList = self.basketballScheduleCrawling()
        for data in dataList:
            if (data["dateForSearch"] == search):
                # 경기일정이 있을 때
                if (data.get('time') != '-'):
                    # 끝나거나, 진행 중인 경기일 때
                    if (data.get('homeScore') != '-'):
                        # 홈 팀이 이겼을 떄
                        if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                        # 원정 팀이 이겼을 때
                        if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                    # 경기가 취소됐을 때
                    elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                        ans += f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                    # 진행 예정인 경기일 때
                    else:
                        ans += f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"

                # 경기 일정이 없을 때
                else:
                    ans += f"{data.get('date')}요일 경기 일정은 없습니다.\n"
        return ans
    
    def basketballTeamSchedule(self,date,teamname):
        ans = ""
        offSeason = [6, 7, 8, 9]
        # 오프시즌일 때
        if date.month in offSeason:
            ans += f"{date}일은 시즌 중의 날짜가 아닙니다.\n"
            return ans
        date = date.strftime("%Y-%m-%d")
        dataList = self.basketballScheduleCrawling()
        for data in dataList:
            if (data["dateForSearch"] == date):
                if (data.get("home") == teamname or data.get("away") == teamname):
                    # 경기일정이 있을 때
                    if (data.get('time') != '-'):
                        # 끝나거나, 진행 중인 경기일 때
                        if (data.get('homeScore') != '-'):
                            # 홈 팀이 이겼을 떄
                            if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                            # 원정 팀이 이겼을 때
                            if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                        # 경기가 취소됐을 때
                        elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                            ans = f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                        # 진행 예정인 경기일 때
                        else:
                            ans = f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"

                    # 경기 일정이 없을 때
            if (ans == ""):
                ans = f"{date}일의 {teamname}팀의 일정은 없습니다\n"
        return ans

    def basketballTeamdataCrawling(self):
        url = f"https://sports.news.naver.com/basketball/record/index?category=kbl"
        res = requests.get(url)
        res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

        soup = BeautifulSoup(res.text, "lxml")
        soupData = soup.find("tbody", {"id": "regularTeamRecordList_table"})
        dataList = []  # 모든 순위정보 저장 리스트
        for data in soupData.findAll("tr"):
            teamData = {}  # 순위 정보 저장 딕셔너리
            # 팀 순위
            teamData["rank"] = data.findAll("strong")[0].text
            # 팀 이름
            teamData["team"] = data.findAll("span")[1].text
            # 경기수
            teamData["total"] = data.findAll("span")[2].text
            # 승리수
            teamData["win"] = data.findAll("span")[3].text
            # 패배수
            teamData["lose"] = data.findAll("span")[4].text
            # 승률
            teamData["winRate"] = data.findAll("strong")[1].text
            # 승차
            teamData["difference"] = data.findAll("span")[5].text
            # 득점
            teamData["points"] = data.findAll("span")[6].text
            # 어시스트
            teamData["assist"] = data.findAll("span")[7].text
            # 리바운드
            teamData["rebound"] = data.findAll("span")[8].text
            # 스틸
            teamData["steal"] = data.findAll("span")[9].text
            # 블록
            teamData["block"] = data.findAll("span")[10].text
            # 3점슛
            teamData["threePoint"] = data.findAll("span")[11].text
            # 자유투
            teamData["freethrow"] = data.findAll("span")[12].text
            # 자유투 성공률
            teamData["freethrowPer"] = data.findAll("span")[13].text
            dataList.append(teamData)
        return dataList

    def basketballTeamdata(self, team):
        dataList = self.basketballTeamdataCrawling()
        for data in dataList:
            if (data['team'].replace(" ", "") == team.replace(" ", "")):
                ans = f"{data.get('team')}의 순위는 {data.get('rank')}위입니다.\n" \
                      f"현재 {data.get('total')}전 {data.get('win')}승 {data.get('lose')}패를 기록 중으로 " \
                      f"승률은 {round(float(data.get('winRate')),2) * 100}%\n 1위와 {data.get('difference')} 게임차입니다.\n\n" \
                      f"팀 데이터\n" \
                      f"득점: {data.get('points')} 어시스트: {data.get('assist')} 리바운드: {data.get('rebound')} 스틸: {data.get('steal')} 블로킹: {data.get('block')}\n" \
                      f"3점 슛: {data.get('threePoint')} 자유투: {data.get('freethrow')} 자유투 성공률: {data.get('freethrowPer')}"
                break
            else:
                ans = "해당 팀은 존재하지 않습니다."
        return ans

    def basketballRanking(self):
        dataList = self.basketballTeamdataCrawling()
        ans = "순위\t팀\t경기수\t승\t패\t게임차\n"
        for data in dataList:
            ans += f" {data.get('rank')}\t{data.get('team')}\t{data.get('total')}\t" \
                   f"{data.get('win')}\t{data.get('lose')}\t{data.get('difference')}\n"
        return ans

    def americaBasketballScheduleCrawling(self):
        months = [self.month]
        dataList = []
        for month in months:
            url = f"https://sports.news.naver.com/basketball/schedule/index?date=20221001&month={month}&year=2022&teamCode=&category=nba"
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

            soup = BeautifulSoup(res.text, "lxml")
            soupData = [soup.findAll("div", {"class": "sch_tb"}), soup.findAll("div", {"class": "sch_tb2"})]  # 짝수, 홀수
            for dataTb in soupData:
                for data in dataTb:
                    # 모든 날짜
                    dateValue = data.find("span", {"class": "td_date"}).text

                    # input을 위한 날짜 정규화
                    dateValue2 = data.find("strong").text
                    dateValue2 = dateValue2.split(".")
                    if (int(dateValue2[0]) < 10):
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-0{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-0{dateValue2[0]}-{dateValue2[1]}"
                    else:
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-{dateValue2[0]}-{dateValue2[1]}"

                    if (len(dateValue.split(" ")[0].split(".")[1]) == 1):
                        dateValue = dateValue.split(" ")[0].split(".")[0] + ".0" + dateValue.split(" ")[0].split(".")[
                            1] + " " + dateValue.split(" ")[1]

                    matchNum = data.find("td")["rowspan"]  # 경기가 없는 날의 rowspan == 5, 있는 날의 rowspan은 경기수
                    if (int(matchNum) == 5):
                        matchNum = '1'
                    for i in range(int(matchNum)):
                        matchData = {}  # 모든 경기정보 저장하는 딕셔너리
                        # 날짜
                        matchData["date"] = dateValue
                        matchData["dateForSearch"] = dateValue2
                        # 시간
                        matchData["time"] = data.findAll("tr")[i].find("span", {"class": "td_hour"}).text
                        if matchData["time"] != "-":  # 경기 일정이 있을때
                            # 홈팀
                            matchData["home"] = data.findAll("tr")[i].find("span", {"class": "team_rgt"}).text
                            # 어웨이팀
                            matchData["away"] = data.findAll("tr")[i].find("span", {"class": "team_lft"}).text
                            # VS일 시 무승부나 진행예정경기
                            if data.findAll("tr")[i].find("strong", {"class": "td_score"}).text != "VS":  # 종료된 경기일 때
                                # 홈팀 스코어
                                matchData["homeScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[1]
                                # 어웨이팀 스코어
                                matchData["awayScore"] = \
                                    data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[0]
                            else:  # 진행 예정 경기일 떄
                                matchData["homeScore"] = "-"
                                matchData["awayScore"] = "-"
                            # 경기장
                            matchData["stadium"] = data.findAll("tr")[i].findAll("span", {"class": "td_stadium"})[
                                0].text
                        else:  # 경기 일정이 없을 시
                            matchData["home"] = "-"
                            matchData["away"] = "-"
                            matchData["homeScore"] = "-"
                            matchData["awayScore"] = "-"
                            matchData["stadium"] = "-"
                        dataList.append(matchData)
        return dataList

    def americaBasketballSchedule(self, search):
        ans = ""
        offSeason = [7, 8, 9]
        # 오프시즌일 때
        if search.month in offSeason:
            ans += f"{search}일은 시즌 중의 날짜가 아닙니다.\n"
            return ans
        dataList = self.americaBasketballScheduleCrawling()
        search = search.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == search):
                # 경기일정이 있을 때
                if (data.get('time') != '-'):
                    # 끝나거나, 진행 중인 경기일 때
                    if (data.get('homeScore') != '-'):
                        # 홈 팀이 이겼을 떄
                        if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                        # 원정 팀이 이겼을 때
                        if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                    # 경기가 취소됐을 때
                    elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                        ans += f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                    # 진행 예정인 경기일 때
                    else:
                        ans += f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"

                # 경기 일정이 없을 때
                else:
                    ans += f"{data.get('date')}요일 경기 일정은 없습니다.\n"
        return ans
    
    def americaBasketballTeamSchedule(self,date,teamname):
        ans = ""
        offSeason = [7, 8, 9]
        # 오프시즌일 때
        if date.month in offSeason:
            ans += f"{date}일은 시즌 중의 날짜가 아닙니다.\n"
            return ans
        dataList = self.americaBasketballScheduleCrawling()
        search = date.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == search):
                if (data.get("home") == teamname or data.get("away") == teamname):
                    # 경기일정이 있을 때
                    if (data.get('time') != '-'):
                        # 끝나거나, 진행 중인 경기일 때
                        if (data.get('homeScore') != '-'):
                            # 홈 팀이 이겼을 떄
                            if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                            # 원정 팀이 이겼을 때
                            if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                                ans = f"{data.get('date')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                        # 경기가 취소됐을 때
                        elif (data.get('platform') == "해당 경기는 현지 사정으로 취소되었습니다."):
                            ans = f"{data.get('date')} {data.get('time')}에 {data.get('stadium')}경기장에서 진행 될 (홈){data.get('home')} VS {data.get('away')}(원정) {data.get('platform')}\n"
                        # 진행 예정인 경기일 때
                        else:
                            ans = f"{data.get('date')} 일정은 {data.get('time')}에\n(홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"
            if (ans == ""):
                ans = f"{date}일의 {teamname}팀의 일정은 없습니다\n"

        return ans


    def americaBasketballTeamdataCrawling(self):
        locations = ["EAST", "WEST"]
        dataList = []  # 모든 순위정보 저장 리스트
        for location in locations:
            url = f"https://sports.news.naver.com/basketball/record/index?category=nba&year=2023&conference={location}"
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

            soup = BeautifulSoup(res.text, "lxml")
            soupData = soup.find("tbody", {"id": "regularTeamRecordList_table"})
            for data in soupData.findAll("tr"):
                teamData = {}  # 순위 정보 저장 딕셔너리
                # 팀 순위
                teamData["rank"] = data.findAll("strong")[0].text
                # 팀 이름
                teamData["team"] = data.findAll("span")[1].text
                # 디비전
                teamData["division"] = data.findAll("span")[2].text
                # 경기수
                teamData["total"] = data.findAll("span")[3].text
                # 승리수
                teamData["win"] = data.findAll("span")[4].text
                # 패배수
                teamData["lose"] = data.findAll("span")[5].text
                # 승률
                teamData["winRate"] = data.findAll("strong")[1].text
                # 승차
                teamData["difference"] = data.findAll("span")[6].text
                # 홈승
                teamData["homeWin"] = data.findAll("span")[7].text
                # 홈패
                teamData["homeLose"] = data.findAll("span")[8].text
                # 원정승
                teamData["awayWin"] = data.findAll("span")[9].text
                # 원정패
                teamData["awayLose"] = data.findAll("span")[10].text
                # 디비전승
                teamData["divisionWin"] = data.findAll("span")[11].text
                # 디비전패
                teamData["divisionLose"] = data.findAll("span")[12].text
                # 연속
                teamData["winStreak"] = data.findAll("span")[13].text
                dataList.append(teamData)
        return dataList

    def americaBasketballTeamdata(self, team):
        dataList = self.americaBasketballTeamdataCrawling()
        for data in dataList:
            if (data['team'].replace(" ", "") == team.replace(" ", "")):
                ans = f"{data.get('division')}디비전 {data.get('team')}의 순위는 {data.get('rank')}위입니다.\n" \
                      f"현재 {data.get('total')}전 {data.get('win')}승 {data.get('lose')}패를 기록 중으로 " \
                      f"승률은 {round(float(data.get('winRate')) * 100, 3)}%\n 1위와 {data.get('difference')} 게임차입니다.\n" \
                      f"홈 승: {data.get('homeWin')}승 홈 패: {data.get('homeLose')}패 원정 승: {data.get('awayWin')}승 원정 패: {data.get('awayLose')}패 연속: {data.get('winStreak')} "
                break
            else:
                ans = "해당 팀은 존재하지 않습니다."
        return ans

    def americaBasketballRanking(self):
        dataList = self.americaBasketballTeamdataCrawling()
        cnt = 0
        ans = "=============동부=============\n\n"
        ans += "순위\t팀\t경기수\t승\t패\t게임차\n"
        for data in dataList:
            ans += f" {data.get('rank')}\t{data.get('team')}\t{data.get('total')}\t" \
                   f"{data.get('win')}\t{data.get('lose')}\t{data.get('difference')}\n"
            cnt += 1
            if (cnt == 15):
                ans += "=============서부=============\n\n"
        return ans

    def vollyballScheduleCrawling(self):
        
        months = [self.month]
        if (self.day <= 14):
            months = [self.month - 1, self.month]
        elif(self.day >= 17):
            months = [self.month,self.month+1]
        dataList = []
        for month in months:
            url = f"https://sports.news.naver.com/volleyball/schedule/index?date=20221004&month={month}&year=2022&teamCode=&category="
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

            soup = BeautifulSoup(res.text, "lxml")
            soupData = [soup.findAll("div", {"class": "sch_tb"}),
                        soup.findAll("div", {"class": "sch_tb2"})]  # sch_tb 짝수날짜, sch_tb2 홀수날짜
            for dataTb in soupData:
                for data in dataTb:
                    # 모든 날짜
                    dateValue = data.find("span", {"class": "td_date"}).text
                    # input을 위한 날짜 정규화
                    dateValue2 = data.find("strong").text
                    dateValue2 = dateValue2.split(".")
                    if (int(dateValue2[0]) < 10):
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-0{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-0{dateValue2[0]}-{dateValue2[1]}"
                    else:
                        if (int(dateValue2[1]) > 0 and int(dateValue2[1]) < 10):
                            dateValue2 = f"2022-{dateValue2[0]}-0{dateValue2[1]}"
                        else:
                            dateValue2 = f"2022-{dateValue2[0]}-{dateValue2[1]}"

                    if (len(dateValue.split(" ")[0].split(".")[1]) == 1):
                        dateValue = dateValue.split(" ")[0].split(".")[0] + ".0" + dateValue.split(" ")[0].split(".")[
                            1] + " " + dateValue.split(" ")[1]
                    matchNum = data.find("td")["rowspan"]  # 경기가 없는 날의 rowspan == 5, 있는 날의 rowspan은 경기수
                    if (int(matchNum) == 5):
                        matchNum = '1'
                    for i in range(int(matchNum)):
                        matchData = {}  # 경기정보를 저장하는 딕셔너리
                        # 날짜정보
                        matchData["date"] = dateValue
                        matchData["dateForSearch"] = dateValue2
                        # 경기시간
                        matchData["time"] = data.findAll("tr")[i].find("span", {"class": "td_hour"}).text
                        if matchData["time"] != "-":  # 경기 일정이 있을때
                            # 홈팀
                            matchData["home"] = data.findAll("tr")[i].find("span", {"class": "team_lft"}).text
                            # 어웨이팀
                            matchData["away"] = data.findAll("tr")[i].find("span", {"class": "team_rgt"}).text
                            if data.findAll("tr")[i].find("strong", {"class": "td_score"}).text != "VS":  # 종료된 경기일 때
                                # 홈팀 스코어
                                matchData["homeScore"] = \
                                data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[0]
                                # 어웨이팀 스코어
                                matchData["awayScore"] = \
                                data.findAll("tr")[i].find("strong", {"class": "td_score"}).text.split(":")[1]
                            else:  # 진행 예정 경기일 떄
                                matchData["homeScore"] = "-"
                                matchData["awayScore"] = "-"
                            # 남성부 / 여성부 경기
                            matchData["gender"] = data.findAll("tr")[i].findAll("span", {"class": "td_event"})[0].text
                            # 경기장
                            matchData["stadium"] = data.findAll("tr")[i].findAll("span", {"class": "td_stadium"})[
                                0].text
                            # 라운드
                            matchData["round"] = data.findAll("tr")[i].findAll("span", {"class": "td_round"})[0].text
                        else:  # 경기 일정이 없을 시
                            matchData["home"] = "-"
                            matchData["away"] = "-"
                            matchData["homeScore"] = "-"
                            matchData["awayScore"] = "-"
                            matchData["gender"] = "-"
                            matchData["stadium"] = "-"
                            matchData["round"] = "-"
                        dataList.append(matchData)
        return dataList

    def vollyballSchedule(self, search):
        ans = ""
        offSeason = [5, 6, 7]
        # 오프시즌일 때
        if search.month in offSeason:
            ans += f"{search}일은 시즌 중의 날짜가 아닙니다."
            return ans
        dataList = self.vollyballScheduleCrawling()
        search = search.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == search):
                # 경기일정이 있을 때
                if (data.get('time') != '-'):
                    if (data.get("gender") == "남자부"):
                        ans += "=========== 남성부 ===========\n"
                    if (data.get("gender") == "여자부"):
                        ans += "=========== 여성부 ===========\n"
                    # 끝나거나, 진행 중인 경기일 때
                    if (data.get('homeScore') != '-'):
                        # 홈 팀이 이겼을 떄
                        if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 진행된 {data.get('round')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                        # 원정 팀이 이겼을 때
                        if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                            ans += f"{data.get('date')} 진행된 {data.get('round')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                    # 진행 예정인 경기일 때
                    else:
                        ans += f"{data.get('date')} {data.get('round')}일정은 \n" \
                               f"{data.get('time')}에 (홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"

                # 경기 일정이 없을 때
                else:
                    ans += f"{data.get('date')}요일 경기 일정은 없습니다.\n"
        return ans

    def vollyballTeamSchedule(self, date, teamname):
        ans = ""
        offSeason = [5, 6, 7]
        # 오프시즌일 때
        if date.month in offSeason:
            ans += f"{date}일은 시즌 중의 날짜가 아닙니다."
            return ans
        dataList = self.vollyballScheduleCrawling()
        date = date.strftime("%Y-%m-%d")
        for data in dataList:
            if (data["dateForSearch"] == date):
                if (data.get("home") == teamname or data.get("away") == teamname):
                    # 경기일정이 있을 때
                    if (data.get('time') != '-'):
                        # 끝나거나, 진행 중인 경기일 때
                        if (data.get('homeScore') != '-'):
                            # 홈 팀이 이겼을 떄
                            if (int(data.get('homeScore')) > int(data.get('awayScore'))):
                                ans += f"{data.get('date')} 진행된 {data.get('round')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 홈팀 {data.get('home')}이(가) 승리하였습니다\n"

                            # 원정 팀이 이겼을 때
                            if (int(data.get('homeScore')) < int(data.get('awayScore'))):
                                ans += f"{data.get('date')} 진행된 {data.get('round')} 경기\n(홈){data.get('home')} {data.get('homeScore')} : {data.get('awayScore')} {data.get('away')}(원정) 으로 원정팀 {data.get('away')}이(가) 승리하였습니다\n"

                        # 진행 예정인 경기일 때
                        else:
                            ans += f"{data.get('date')} {data.get('round')}일정은 \n" \
                                   f"{data.get('time')}에 (홈){data.get('home')} VS {data.get('away')}(원정) 경기가 {data.get('stadium')}경기장에서 진행될 예정입니다.\n"

            if (ans == ""):
                ans = f"{date}일의 {teamname}팀의 일정은 없습니다\n"
        return ans
    
    def vollyballTeamdataCrawling(self):
        genders = ["kovo", "wkovo"]
        dataList = []  # 모든 순위정보 저장 리스트
        for gender in genders:
            url = f"https://sports.news.naver.com/volleyball/record/index?category={gender}&year=2022"
            res = requests.get(url)
            res.raise_for_status()  # 웹 정보를 못 불러왔을 경우 오류 출력

            soup = BeautifulSoup(res.text, "lxml")
            soupData = soup.find("tbody", {"id": "regularTeamRecordList_table"})

            for data in soupData.findAll("tr"):
                ans = ""
                teamData = {}  # 순위 정보 저장 딕셔너리
                # 팀 순위
                teamData["rank"] = data.findAll('strong')[0].text
                # 팀 이름
                teamData["team"] = data.findAll("span")[1].text
                # 경기수
                teamData["total"] = data.findAll("span")[2].text
                # 승리수
                teamData["win"] = data.findAll("span")[3].text
                # 패배수
                teamData["lose"] = data.findAll("span")[4].text
                # 세트득실률
                teamData["setScore"] = data.findAll("span")[5].text
                # 점수 득실률
                teamData["pointPer"] = data.findAll("span")[6].text
                # 세트수
                teamData["set"] = data.findAll("span")[7].text
                # 공격 성공률
                teamData["attackPer"] = data.findAll("span")[8].text
                # 블로킹
                teamData["blocking"] = data.findAll("span")[9].text
                # 서브
                teamData["serve"] = data.findAll("span")[10].text
                # 득점
                teamData["score"] = data.findAll("span")[11].text
                dataList.append(teamData)
        return dataList

    def vollyballTeamdata(self, team):
        ans = ""
        dataList = self.vollyballTeamdataCrawling()
        for data in dataList:
            if (data["team"].replace(" ", "") == team.replace(" ", "")):
                ans = f"{data.get('team')}의 순위는 {data.get('rank')}위입니다.\n" \
                      f"현재 {data.get('total')}전 {data.get('win')}승 {data.get('lose')}패를 기록 중입니다.\n\n" \
                      f"=========== 팀 데이터 ===========\n" \
                      f"세트: {data.get('set')} 세트득실률: {data.get('setScore')} 점수득실률: {data.get('pointPer')}\n" \
                      f"공격성공률: {data.get('attackPer')} 블로킹: {data.get('blocking')} 서브: {data.get('serve')} 득점: {data.get('score')}"
                break
            else:
                ans = "해당 팀은 존재하지 않습니다."
        return ans

    def vollyballRanking(self):
        dataList = self.vollyballTeamdataCrawling()
        cnt = 0
        ans = "=============남성부=============\n"
        ans += "순위\t팀\t경기수\t승\t패\n"
        for data in dataList:
            ans += f" {data.get('rank')}\t{data.get('team')}\t{data.get('total')}\t" \
                   f"{data.get('win')}\t{data.get('lose')}\n"
            cnt += 1
            if (cnt == 7):
                ans += "=============여성부=============\n"
        return ans

    def week(self, args, week, defname):
        result = []
        answer = ""
        if (args == 0):
            for i in range(1, 7):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 1):
            for i in range(0, 6):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 2):
            for i in range(-1, 5):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 3):
            for i in range(-2, 4):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 4):
            for i in range(-3, 3):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 5):
            for i in range(-4, 2):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        if (args == 6):
            for i in range(-5, 1):
                result.append(defname(dt.date.today() + timedelta(i + week)) + "\n")
        answer = ''.join(result)
        return answer
    
    def teamWeek(self, args, week, defname, teamname):
        result = []
        answer = ""
        if (args == 0):
            for i in range(1, 7):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 1):
            for i in range(0, 6):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 2):
            for i in range(-1, 5):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 3):
            for i in range(-2, 4):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 4):
            for i in range(-3, 3):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 5):
            for i in range(-4, 2):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        if (args == 6):
            for i in range(-5, 1):
                result.append(defname(dt.date.today() + timedelta(i + week),teamname) + "\n")
        answer = ''.join(result)
        return answer

    def sport(self, req):
        answer = ""
        params = req['action']['detailParams']  # 사용자가 전송한 실제 메시지
        baseball_params = ["KBO", "kbo", "크보", "야구"]
        basketball_params = ["KBL", "kbl", "크블", "한농", "농구"]
        vollyball_params = ["KV", "kv", "한배", "여배", "남배","배구"]
        america_basketball_params = ["nba", "NBA", "느바", "미국농구", "외국농구", "외농"]
        # print(params['sports_league']['value'])
        # 일정 조회
        
        #if 'sports_league' in params.keys():
        # 야구일때
        if (params['sports_league']['value'] in baseball_params):
            if 'sys_date' in params.keys():
                inputs = dt.date.today() + timedelta()
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamSchedule(inputs,teamname)
                else:
                    answer = self.baseballSchedule(inputs)
            if 'tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(1)
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamSchedule(inputs,teamname)
                else:
                    answer = self.baseballSchedule(inputs)
            if 'after_tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(2)
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamSchedule(inputs,teamname)
                else:
                    answer = self.baseballSchedule(inputs)
            if 'match_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(1)
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamSchedule(inputs,teamname)
                else:
                    answer = self.baseballSchedule(inputs)
            if 'match_before_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(2)
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamSchedule(inputs,teamname)
                else:
                    answer = self.baseballSchedule(inputs)

            if 'this_week' in params.keys():
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.teamWeek(self.week_idx,0,self.baseballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 0, self.baseballSchedule)
            if 'match_before_week' in params.keys():
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.teamWeek(self.week_idx,-7,self.baseballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, -7, self.baseballSchedule)
            if 'week_next' in params.keys():
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.teamWeek(self.week_idx,7,self.baseballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 7, self.baseballSchedule)

            if 'sports_rank' in params.keys():
                if 'sports_baseball_team' in params.keys():
                    teamname = params['sports_baseball_team']['value']
                    answer = self.baseballTeamData(teamname.upper())
                else:
                    answer = self.baseballRanking()

        # 한국농구 일 때
        if (params['sports_league']['value'] in basketball_params):
            if 'sys_date' in params.keys():
                inputs = dt.date.today() + timedelta()
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.basketballSchedule(inputs)
            if 'tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(1)
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.basketballSchedule(inputs)
            if 'after_tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(2)
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.basketballSchedule(inputs)
            if 'match_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(1)
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.basketballSchedule(inputs)
            if 'match_before_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(2)
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.basketballSchedule(inputs)

            if 'this_week' in params.keys():
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.teamWeek(self.week_idx,0,self.basketballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 0, self.basketballSchedule)
            if 'match_before_week' in params.keys():
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.teamWeek(self.week_idx,-7,self.basketballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, -7, self.basketballSchedule)
            if 'week_next' in params.keys():
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.teamWeek(self.week_idx,7,self.basketballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 7, self.basketballSchedule)


            if 'sports_rank' in params.keys():
                if 'sports_basketball_team' in params.keys():
                    teamname = params['sports_basketball_team']['value']
                    answer = self.basketballTeamdata(teamname.upper())
                else :
                    answer = self.basketballRanking()
        # nba 일떄
        if (params['sports_league']['value'] in america_basketball_params):
            if 'sys_date' in params.keys():
                inputs = dt.date.today() + timedelta()
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.americaBasketballSchedule(inputs)
            if 'tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(1)
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.americaBasketballSchedule(inputs)
            if 'after_tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(2)
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.americaBasketballSchedule(inputs)
            if 'match_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(1)
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.americaBasketballSchedule(inputs)
            if 'match_before_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(2)
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamSchedule(inputs,teamname)
                else:
                    answer = self.americaBasketballSchedule(inputs)

            if 'sports_rank' in params.keys():
                if 'sports_USAbasketball_team' in params.keys():
                    teamname = params['sports_USAbasketball_team']['value']
                    answer = self.americaBasketballTeamdata(teamname.upper())
                else:
                    answer = self.americaBasketballRanking()


        #배구일 때
        if (params['sports_league']['value'] in vollyball_params):
            if 'sys_date' in params.keys():
                inputs = dt.date.today() + timedelta()
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamSchedule(inputs,teamname)
                else:
                    answer = self.vollyballSchedule(inputs)
            if 'tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(1)
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamSchedule(inputs,teamname)
                else:
                    answer = self.vollyballSchedule(inputs)
            if 'after_tomorrow' in params.keys():
                inputs = dt.date.today() + timedelta(2)
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamSchedule(inputs,teamname)
                else:
                    answer = self.vollyballSchedule(inputs)
            if 'match_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(1)
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamSchedule(inputs,teamname)
                else:
                    answer = self.vollyballSchedule(inputs)
            if 'match_before_yesterday' in params.keys():
                inputs = dt.date.today() - timedelta(2)
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamSchedule(inputs,teamname)
                else:
                    answer = self.vollyballSchedule(inputs)

            if 'this_week' in params.keys():
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.teamWeek(self.week_idx,0,self.vollyballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 0, self.vollyballSchedule)
            if 'match_before_week' in params.keys():
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.teamWeek(self.week_idx,-7,self.vollyballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, -7, self.vollyballSchedule)
            if 'week_next' in params.keys():
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.teamWeek(self.week_idx,7,self.vollyballTeamSchedule,teamname)
                else :
                    answer = self.week(self.week_idx, 7, self.vollyballSchedule)

            if 'sports_rank' in params.keys():
                if 'sports_vollyball_team' in params.keys():
                    teamname = params['sports_vollyball_team']['value']
                    answer = self.vollyballTeamdata(teamname.upper())
                else:
                    answer = self.vollyballRanking()

        return answer

