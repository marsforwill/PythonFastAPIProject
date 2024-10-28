from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import requests
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Dict
import string
import random

app = FastAPI()

def fetch_bond_announcements(date: str):
    # 配置请求的 URL 和查询参数
    url = "https://query.sse.com.cn/commonSoaQuery.do"
    params = {
        "jsonCallBack": "jsonpCallback",
        "isPagination": "true",
        "pageHelp.pageSize": 25,
        "pageHelp.cacheSize": 1,
        "type": "inParams",
        "sqlId": "BS_ZQ_GGLL",
        "sseDate": f"{date} 00:00:00",       # 查询开始日期
        "sseDateEnd": f"{date} 23:59:59",     # 查询结束日期
        "bondType": "CORPORATE_BOND_BULLETIN,COMPANY_BOND_BULLETIN",
        "pageHelp.pageNo": 1,
        "pageHelp.beginPage": 1,
        "pageHelp.endPage": 1,
        "_": int(datetime.now().timestamp() * 1000)  # 防缓存时间戳
    }

    # 配置请求头，模拟浏览器请求
    headers = {
        "Referer": "https://www.sse.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    # 发送请求
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        # 去除 JSONP 包装并解析 JSON 数据
        content = response.text
        json_data = json.loads(content[content.index("(") + 1 : content.rindex(")")])
        
        # 提取公告信息
        announcements = json_data["pageHelp"]["data"]
        return announcements

    print("Error:", response.status_code)
    return None

@app.get("/announcements")
async def get_announcements(date: str = Query(..., description="查询公告的日期, 格式为 YYYY-MM-DD")):
    announcements = fetch_bond_announcements(date)
    if announcements:
        # 构建返回数据
        return [
             {
                "fileName": announcement.get("fileName"),
                "securityCode": announcement.get("securityCode"),
                "sseDate": announcement.get("sseDate"),
                "title": announcement.get("title"),
                "url": f"https://www.sse.com.cn{announcement['url']}",
                "keyWord": announcement.get("keyWord", ""),
                "bulletinType": announcement.get("bulletinType"),
                "bulletinHeading": announcement.get("bulletinHeading"),
                "orgBulletinType": announcement.get("orgBulletinType"),
                "securityAbbr": announcement.get("securityAbbr"),
                "bulletinId": announcement.get("bulletinId"),
                "orgFileType": announcement.get("orgFileType"),
                "orgBulletinId": announcement.get("orgBulletinId"),
                "bulletinYear": announcement.get("bulletinYear"),
                "createTime": announcement.get("createTime"),
                "bondType": announcement.get("bondType"),
                "orgBulletinTypeDesc": announcement.get("orgBulletinTypeDesc")
            }
            for announcement in announcements
        ]
    else:
        return {"message": "未找到该日期的公告"}

# 数据库存储 (可以改成持久化数据库，如SQL或NoSQL)
url_db: Dict[str, str] = {}
reverse_url_db: Dict[str, str] = {}

# 基础URL，用于生成短链接
BASE_URL = "http://short.ly/"


# 生成唯一的短链接标识符
def generate_short_id(length=6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.get("/shorten")
async def shorten_url(url: str = Query(..., description="长链接")):
    # 检查URL是否已存在
    if url in reverse_url_db:
        short_id = reverse_url_db[url]
    else:
        # 生成新的短链接ID并存储
        short_id = generate_short_id()
        while short_id in url_db:
            short_id = generate_short_id()
        url_db[short_id] = url
        reverse_url_db[url] = short_id

    short_url = BASE_URL + short_id
    return {"short_url": short_url}

@app.get("/expand")
async def expand_url(short_url: str = Query(..., description="短链接")):
    # 去除基础URL部分，获取短链接ID
    short_id = short_url.replace(BASE_URL, "")
    
    # 查找原始URL
    long_url = url_db.get(short_id)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return {"long_url": long_url}


# 启动应用时的代码入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
