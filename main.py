import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_INFO = {
    'username': os.environ.get("USERNAME"),
    'password': os.environ.get("PASSWORD")
}

with requests.Session() as s:
    df = pd.DataFrame(np.arange(0, 900).reshape(30, 30))
    df = df.astype(str)

    df.columns = os.environ.get("STUDENT_LIST").split("-")
    df.index = os.environ.get("STUDENT_LIST").split("-")

    for col in df.columns:
        df[col].values[:] = ""

    login_req = s.post(os.environ.get("GEL_LOGIN_URL"), data=LOGIN_INFO)
    print(login_req.status_code, "- GEL 접속 성공!")

    url = '주소를 입력해주세요!'
    response = s.get(url)

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    result = soup.select('section#region-main > div table > tbody > tr.discussion')

    for idx, r in enumerate(result):
        author_name = r.select_one('td:nth-child(3) > a:nth-child(1)').get_text()
        article = r.select_one('td:nth-child(1) > a:nth-child(1)')

        print(f"({idx+1}/30) {author_name}: {article.getText()}")

        article_url = article['href']
        response = s.get(article_url).content
        soup = BeautifulSoup(response, 'html.parser')

        reply_list = soup.select('section#region-main > div > div.indent')
        
        for reply in reply_list:
            date = reply.select_one('div.author').get_text()[:-8]
            reply_name = reply.select_one('div.author a').get_text()
            if reply_name == os.environ.get("PROFESSOR"):
                continue

            reply_content = reply.select_one('div.maincontent div.posting')
            
            df.at[reply_name, author_name] = f"{date}\n\n{reply_content.get_text()}"

    subject = soup.select_one("section#region-main h2").get_text()

    df.to_csv(f'./{subject}.csv', sep=',', na_rep='NaN')
    print(f"{subject}.csv 생성 완료!")
