"""复刻 CommentSpider 的请求逻辑，独立可跑，方便对照 123.py 调试"""
import httpx
import json

# ========== 改这里 ==========
NOTE_ID = "69c8d23a0000000022029f86"
XSEC_TOKEN = "ABADA7CjO0NtR4Ig-RJxv15-wsUb_eM-aUr6W3N4l3qis"
WEB_SESSION = "0400698f876588565e4bf94be33b4b292e0dce"  # 替换成最新的
# ===========================

URL = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "origin": "https://www.xiaohongshu.com",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

COOKIES = {
    "web_session": WEB_SESSION,
}

PARAMS = {
    "note_id": NOTE_ID,
    "cursor": "",
    "top_comment_id": "",
    "image_formats": "jpg,webp,avif",
    "xsec_token": XSEC_TOKEN,
}


def main():
    print(f"URL    : {URL}")
    print(f"PARAMS : {PARAMS}")
    print(f"COOKIES: {COOKIES}")
    print("-" * 60)

    r = httpx.get(URL, headers=HEADERS, cookies=COOKIES, params=PARAMS, timeout=15)
    print(f"status : {r.status_code}")
    print(f"resp   : {r.text[:1000]}")
    try:
        data = r.json()
        print("-" * 60)
        print("code   :", data.get("code"))
        print("msg    :", data.get("msg"))
        print("comments count:", len((data.get("data") or {}).get("comments") or []))
    except Exception as e:
        print(f"JSON 解析失败: {e}")


if __name__ == "__main__":
    main()
