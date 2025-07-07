
from loguru import logger
import requests
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage
import test
class Page:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        }
    def get_page(self,page):
        next_url_title_dict = {}
        url = f"https://zh.z-library.sk/s/%E5%8F%8C%E8%AF%AD?languages%5B0%5D=chinese&page={page}"
        params = {
            "languages%5B0%5D": "chinese",
            "page": str(page)
        }
        cookies = {
            "siteLanguage": "zh",
            "remix_userkey": "c936f9139d8f71679d4b02435384a6df",
            "remix_userid": "43592460"
        }
        logger.info(f"正在处理第{page}页")
        response = requests.get(url, headers=self.headers, cookies=cookies, params=params)
        soup = BeautifulSoup(response.text, "html.parser")
        # 提取
        for book_div in soup.find_all('div', class_='book-item resItemBoxBooks'):
            bookcard = book_div.find('z-bookcard')
            href = bookcard.get('href', '')
            title_div = bookcard.find('div', slot='title')
            title = title_div.text.strip() if title_div else ''
            next_url_title_dict[title] = "https://zh.z-library.sk"+href
        logger.success("该页的地址以及书名全部采集完成，正在获取其内容下载地址")
        for k,v in next_url_title_dict.items():
            self.get_book(k,v)


    def range(self):
        for i in range(1,100000):
            self.get_page(i)


    def get_book(self, title,url):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://zh.z-library.sk/s/%E5%8F%8C%E8%AF%AD?languages%5B0%5D=chinese&page=1",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
        }
        cookies = {
            "siteLanguage": "zh",
            "remix_userid": "43592460",
            "remix_userkey": "4d82bef9f7f2d6b9e2a33e63038f3130",
            "selectedSiteMode": "books"
        }
        book_name = title
        url = url
        response = requests.get(url, headers=headers, cookies=cookies).text

        soup = BeautifulSoup(response, "html.parser")
        download = {}

        # 找主下载链接
        main_a = soup.find('a', class_='btn btn-default addDownloadedBook')
        if main_a:
            href = main_a.get("href", "")

            ext = main_a.select_one("span.book-property__extension")
            size = main_a.text.split(',')[-1].strip()

            if href and ext:
                key = f"{ext.text.strip()} {size}"  # 例如 epub 553 KB
                download[key] = "http://zh.z-library.sk" + href
        logger.success(f"该书的名字为:{title}")
        for k,v in download.items():
            logger.success(f"格式为{k},下载地址为{v}")
            self.get_download_url(v,k,book_name)

    def get_download_url(self,downurl,typefile,book_name):
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
        url = downurl
        response = requests.get(url, headers=headers, allow_redirects=False)

        type_file = typefile
        book_name = book_name
        headers_dict = dict(response.headers)
        test.fina(headers_dict["Location"],type_file.split(" ")[0],book_name)






if __name__ == '__main__':
    page = Page()
    page.range()
    # page.download('http://zh.z-library.sk/dl/19262022/72a214')