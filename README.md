# 上交所债券公告数据服务与短链接服务

本项目实现了两个核心功能：
1. 从上交所债券公告页面抓取债券公告数据，并根据日期返回公告列表。
2. 提供长链接转短链接和短链接还原长链接的服务。

## 功能概述

### 1. 上交所债券公告数据服务
该服务提供查询上交所债券公告的接口，通过指定日期获取对应的债券公告列表。
- **框架**：FastAPI
- **接口**：通过日期参数查询债券公告。

#### API 使用

- **GET /announcements**
  - **参数**：`date` (string) - 查询日期，格式为 `YYYY-MM-DD`
  - **示例请求**：
    ```
    GET http://127.0.0.1:8000/announcements?date=2024-10-28
    ```
  - **返回示例**：
    ![image](https://github.com/user-attachments/assets/2f5d80b5-8392-48c3-ac4f-2ad50a8678b8)


### 2. 短链接服务
该服务提供长链接转短链接和短链接还原为长链接的功能。
- **框架**：FastAPI
- **接口**：长链接生成短链接，短链接还原为长链接。

#### API 使用

- **GET /shorten**
  - **参数**：`url` (string) - 长链接
  - **示例请求**：
    ```
    GET http://127.0.0.1:8000/shorten?url=https://example.com/long-url
    ```
  - **返回示例**：
    ```json
    {
      "short_url": "http://short.ly/abc123"
    }
    ```

- **GET /expand**
  - **参数**：`short_url` (string) - 短链接
  - **示例请求**：
    ```
    GET http://127.0.0.1:8000/expand?short_url=http://short.ly/abc123
    ```
  - **返回示例**：
    ```json
    {
      "long_url": "https://example.com/long-url"
    }
    ```

## 系统设计与扩展性

- **持久化存储**：短链接数据目前为内存存储，获取通告数据接口目前为拼凑实时的请求转发， 后续可以扩展为 SQL 或 NoSQL 数据库以支持更大的数据量和更高的并发性。
- **唯一性生成**：使用随机生成的短链接标识符来确保短链接的唯一性。可扩展为使用分布式 ID 生成算法。
- **前端页面**：可以使用 amis 框架来构建用户界面，用于输入和展示公告查询结果及短链接生成。
  
## 项目结构

```plaintext
.
├── main.py                  # 主服务代码
└── README.md                # 使用说明文档
```

## 项目运行
pip install -r requiremnt.txt
uvicorn main:app --reload 或者 python main.py
