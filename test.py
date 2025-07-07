import os
import re
import requests
from loguru import logger
from tqdm import tqdm
import time

MAX_RETRIES = 5  # 最大重试次数

def fina(url, type_file, book_name):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "Cookie": "siteLanguage=zh; remix_userid=43592460; domainsNotWorking=ddns.ac; remix_userkey=4d82bef9f7f2d6b9e2a33e63038f3130; selectedSiteMode=books",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }

    book_name = re.sub(r'[\\/:*?"<>|]', '_', book_name)
    save_dir = "down_save"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{book_name}.{type_file}")

    if os.path.exists(file_path):
        logger.info(f"《{book_name}》已存在，跳过下载")
        return

    logger.info(f"《{book_name}》开始下载为 .{type_file} 文件")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # 第一次请求，获取跳转地址
            response = requests.get(url, headers=headers, allow_redirects=False, timeout=10)
            print(response.headers)
            if "Location" not in response.headers:
                raise Exception("未找到跳转链接")
            real_url = response.headers["Location"]
        except Exception as e:
            logger.warning(f"第 {attempt} 次第一次请求失败: {e}")
            time.sleep(2)
            continue  # 重试第一次请求

        try:
            # 第二次请求，下载内容
            with requests.get(real_url, headers=headers, stream=True, timeout=20) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))

                with open(file_path, 'wb') as f, tqdm(
                    total=total,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=book_name[:30],
                    mininterval=0.5
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

            logger.success(f"《{book_name}》下载成功，保存为：{file_path}")
            return  # 成功退出
        except Exception as e:
            logger.warning(f"第 {attempt} 次第二次请求失败: {e}")
            time.sleep(2)
            continue  # 重试第二次请求

    logger.error(f"《{book_name}》连续 {MAX_RETRIES} 次尝试失败，已跳过")
