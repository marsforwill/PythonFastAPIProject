from fastapi import FastAPI, Query
from typing import List, Optional
import requests
import json
from datetime import datetime

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

# 启动应用时的代码入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
