"""DrissionPage 浏览器管理：登录态 + cookie 同步 + 取页"""
import json
import time
from pathlib import Path
from typing import Dict
from DrissionPage import ChromiumPage, ChromiumOptions
from config.settings import COOKIE_FILE, XHS_BASE
from utils.logger import get_logger

# 关键 cookie：只要这一个，就视为已登录
KEY_COOKIE = "web_session"


class DPManager:
    def __init__(self, headless: bool = False):

        opts = ChromiumOptions()
        opts.set_local_port(9333)
        opts.incognito()
        if headless:
            opts.headless()
        self.page = ChromiumPage(opts)
        self.log = get_logger("DPManager")
        self._loaded = False
        self._verified = False  # 本进程内是否已验证过登录态

    # ---------- 登录态 ----------
    def is_logged_in(self) -> bool:
        """直接以浏览器当前 cookie 为准；每次跑都用浏览器最新 cookie 覆盖 cookies.json。"""
        # 已经验证过 → 只看 cookie 是否还在，不再做 DOM 检查
        if self._verified:
            ws = self.get_cookies().get(KEY_COOKIE)
            return bool(ws)

        # === 第一轮：从 cookies.json 读 web_session，先注入浏览器再校验 ===
        print("第一轮：从 cookies.json 读取 web_session 校验")
        ws_from_file = self._read_ws_from_file()
        if ws_from_file:
            # 关键顺序：先注入 cookies（冷注入），再导航校验，这样 UI 也是登录态
            self._inject_cookies_into_browser()
            # 确认浏览器里真的有 web_session
            ws_in_browser = self.get_cookies().get(KEY_COOKIE, "")
            if ws_in_browser != ws_from_file:
                print(f"cookie 注入失败（浏览器 ws={ws_in_browser[:20]}），走扫码")
            elif self._verify_via_api(ws_from_file):
                print(f"web_session: {ws_from_file}，cookies.json 有效，API 校验通过")
                self.page.get(f"{XHS_BASE}/explore")
                time.sleep(2)
                if self._has_login_mask():
                    print("⚠ 检测到登录蒙版，UI 未真登录，强制走扫码")
                else:
                    self._save_cookies()
                    self._verified = True
                    return True

        # === 第二轮：用浏览器 profile 当前 cookie 校验 ===
        print("第一轮失败，改用浏览器当前 cookie 再校验一次")
        if XHS_BASE not in (self.page.url or ""):
            self.page.get(f"{XHS_BASE}/explore")
            time.sleep(2)

        ws_from_browser = self.get_cookies().get(KEY_COOKIE)
        if ws_from_browser and ws_from_browser != ws_from_file \
                and self._verify_via_api(ws_from_browser):
            print(f"web_session: {ws_from_browser}，浏览器 cookie API 校验通过")
            # UI 蒙版兜底：导航 explore + 探一下 search_result，任一命中蒙版都判未登录
            self.page.get(f"{XHS_BASE}/explore")
            time.sleep(2)
            mask1 = self._has_login_mask()
            self.page.get(f"{XHS_BASE}/search_result?keyword=test&source=web_explore_feed")
            time.sleep(2)
            mask2 = self._has_login_mask()
            if mask1 or mask2:
                print("⚠ 浏览器 UI 仍有登录蒙版，强制走扫码")
            else:
                self._save_cookies()
                self.log.info(f"已刷新 {COOKIE_FILE.name}")
                self._verified = True
                return True

        print("两轮校验都失败，保留旧 cookies.json，准备扫码登录")
        return False

    def _has_login_mask(self) -> bool:
        """检测当前页面是否存在登录蒙版/扫码弹窗。命中任一选择器即视为未登录。"""
        selectors = [
            ".login-container",
            ".login-modal",
            ".login-box",
            ".reds-mask",
            ".mask.login",
            "div.login-container-wrapper",
            'xpath://*[contains(@class,"login") and contains(@class,"mask")]',
            'xpath://*[contains(@class,"login") and contains(@class,"qrcode")]',
        ]
        for sel in selectors:
            try:
                ele = self.page.ele(sel, timeout=0.5)
                if ele:
                    self.log.info(f"检测到登录蒙版: {sel}")
                    return True
            except Exception:
                continue
        # 兜底：JS 查 body 里是否含登录扫码相关 DOM
        try:
            hit = self.page.run_js(
                "return !!document.querySelector('.login-container,.login-modal,.reds-mask') "
                "|| /登录后查看搜索结果|手机号登录|扫码登录|小红书如何扫码/.test(document.body && document.body.innerText || '');"
            )
            if hit:
                self.log.info("JS 兜底检测到登录蒙版")
                return True
        except Exception:
            pass
        return False

    def _inject_cookies_into_browser(self):
        """冷注入：CDP Network.setCookie 全量写入，然后刷新域页，让 UI 真登录。"""
        if not Path(COOKIE_FILE).exists():
            return
        try:
            arr = json.loads(Path(COOKIE_FILE).read_text(encoding="utf-8"))
            # 先到目标域（空页面也行），确保 CDP 上下文可用
            try:
                self.page.get(f"{XHS_BASE}/favicon.ico")
            except Exception:
                pass
            time.sleep(0.5)
            # 清掉旧 cookie，避免残留的过期 web_session 干扰
            try:
                self.page.run_cdp("Network.clearBrowserCookies")
            except Exception:
                pass
            ok = 0
            for c in arr:
                ck = {
                    "name": c.get("name"),
                    "value": c.get("value", ""),
                    "domain": c.get("domain") or ".xiaohongshu.com",
                    "path": c.get("path") or "/",
                    "secure": bool(c.get("secure", False)),
                    "httpOnly": bool(c.get("httpOnly", False)),
                }
                if c.get("expiry"):
                    ck["expires"] = c["expiry"]
                elif c.get("expires") and isinstance(c["expires"], (int, float)):
                    ck["expires"] = c["expires"]
                if c.get("sameSite") in ("Strict", "Lax", "None"):
                    ck["sameSite"] = c["sameSite"]
                try:
                    self.page.run_cdp("Network.setCookie", **ck)
                    ok += 1
                except Exception as e:
                    self.log.debug(f"setCookie 失败 {ck.get('name')}: {e}")
            self.log.info(f"CDP 注入 {ok}/{len(arr)} 个 cookie")
            # 再导航 explore，让页面带着新 cookie 重新拉取 UI
            self.page.get(f"{XHS_BASE}/explore")
            time.sleep(2)
        except Exception as e:
            self.log.warning(f"注入 cookie 失败: {e}")

    def _read_ws_from_file(self) -> str:
        """从 cookies.json 中提取 web_session（不污染浏览器）。"""
        if not Path(COOKIE_FILE).exists():
            return ""
        try:
            arr = json.loads(Path(COOKIE_FILE).read_text(encoding="utf-8"))
            for c in arr:
                if c.get("name") == KEY_COOKIE:
                    return c.get("value", "")
        except Exception as e:
            self.log.warning(f"读 cookies.json 失败: {e}")
        return ""

    async def login(self):
        """触发扫码：拿到 cookie 即视为成功 → sleep 15s 等蒙版关闭 → 落盘。"""
        print("请扫码登录")
        # 当前页已经有蒙版（自带二维码）就原地扫；否则才导航到 explore
        if not self._has_login_mask():
            self.page.get(f"{XHS_BASE}/explore")

        deadline = time.time() + 120  # 给用户 120s 扫码
        while time.time() < deadline:
            ws = self.get_cookies().get(KEY_COOKIE)
            if ws:
                print("登录成功")
                self.log.info(f"web_session={ws}")

                print("请等待10s")
                time.sleep(10)

                # 刷新页面 + 重新校验
                self.page.refresh()
                time.sleep(2)
                self._verified = False  # 强制重新判定
                if not self.is_logged_in():
                    print("刷新后仍未登录成功，强制退出程序")
                    self.log.error("二次校验失败，退出")
                    import sys
                    sys.exit(1)

                self._save_cookies()
                self.log.info(f"已写入 {COOKIE_FILE.name}")
                self._verified = True
                return
            time.sleep(1)
        raise TimeoutError("等待扫码登录超时（120s）")

    # ---------- cookie ----------
    def get_cookies(self) -> Dict[str, str]:
        return {c["name"]: c["value"] for c in self.page.cookies()}

    def get_key_cookies(self) -> Dict[str, str]:
        """只返回业务必须的 cookie。"""
        all_ck = self.get_cookies()
        return {KEY_COOKIE: all_ck.get(KEY_COOKIE, "")}

    def _save_cookies(self):
        Path(COOKIE_FILE).write_text(
            json.dumps(self.page.cookies(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _try_load_cookies(self):
        if self._loaded or not Path(COOKIE_FILE).exists():
            return
        try:
            cookies = json.loads(Path(COOKIE_FILE).read_text(encoding="utf-8"))
            # DP 设置 cookie 必须先访问对应域
            self.page.get(XHS_BASE)
            self.page.set.cookies(cookies)
            self._loaded = True
            self.log.info(f"已从 {COOKIE_FILE.name} 加载 {len(cookies)} 个 cookie")
        except Exception as e:
            self.log.warning(f"加载 cookie 失败: {e}")

    # ---------- 取页 ----------
    def fetch_html(self, url: str, wait_ele: str = None, timeout: int = 15) -> str:
        self.page.get(url)
        if wait_ele:
            try:
                self.page.wait.ele_displayed(wait_ele, timeout=timeout)
            except Exception:
                pass
        return self.page.html

    # ---------- API 校验 ----------
    def _verify_via_api(self, web_session: str) -> bool:
        """复刻 FeedHarvester：导航到已知笔记详情页，监听 comment API 响应。
        抓到包且 code==0 即视为登录有效。
        """
        note_id = "6831c633000000002301241b"
        xsec_token = "ABuDSsTVLWx3T1h7D74q0zOC76MrpKJCR8p5d9pL27m_E="
        url = (f"{XHS_BASE}/explore/{note_id}"
               f"?xsec_token={xsec_token}&xsec_source=pc_feed")

        self.page.listen.start("/api/sns/web/v2/comment/page")
        try:
            self.page.get(url)
            packet = self.page.listen.wait(count=1, timeout=8, fit_count=False)
            if not packet:
                self.log.info("API 校验：未抓到评论响应 → 失败")
                return False
            if isinstance(packet, list):
                packet = packet[0]
            body = packet.response.body
            if isinstance(body, (bytes, str)):
                try:
                    body = json.loads(body)
                except Exception:
                    body = {}
            code = (body or {}).get("code")
            ok = (code == 0)
            self.log.info(f"API 校验（导航+监听）: code={code} {'通过' if ok else '失败'} | ws={web_session[:20]}...")
            return ok
        except Exception as e:
            self.log.warning(f"API 校验异常: {e}")
            return False
        finally:
            self.page.listen.stop()

    def _verify_via_api_OLD_NOT_USED(self, web_session: str) -> bool:
        """旧版：硬编码 x-s 的 requests 调用，已废弃。"""
        import requests
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://www.xiaohongshu.com",
            "priority": "u=1, i",
            "referer": "https://www.xiaohongshu.com/",
            "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
            "x-b3-traceid": "60c4ccacef9d7b02",
            "x-s": "XYS_2UQhPsHCH0c1PUhAHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlLSQc/oGlpLYEaDEbqemk8rkayrTEp9+awepnJf4x2bSiwrDUy0mP+FDF8o8O8o+oqBRawsRnLgSIpnbsweH3GDRAcdbOJDEEnaVEzSZELS+h/F8+J9RO/MpG4DR6/dDFadS3PDbearlT/MYPJp8mPrkHaMY/+FTpznbTPB8+c9EIqMQCLDkcpnbLP9le8LT/Jfznnfl0yFLIaSQQyAmOarEaLSz+GURDpD+daBbUzgkmyBSm+A88+rHEPsHVHdWFH0ijHdF=",
            "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1PUhAHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjH9N0c1PaHVHdWMH0ijP/DEG9Lh8/DAG0Q3q0P9G/S6qdilwoYk+oWA4AYi80m0G9R7+fWEy7iMPeZIPePEwer7+jHVHdW9H0ijHjIj2eqjwjHjNsQhwsHCHDDAwoQH8B4AyfRI8FS98g+Dpd4daLP3JFSb/BMsn0pSPM87nrldzSzQ2bPAGdb7zgQB8nph8emSy9E0cgk+zSS1qgzianYt8Lzf/LzN4gzaa/+NqMS6qS4HLozoqfQnPbZEp98QyaRSp9P98pSl4oSzcgmca/P78nTTL08z/sVManD9q9z1J9p/8db8aob7JeQl4epsPrz6agW3Lr4ryaRApdz3agYDq7YM47HFqgzkanYMGLSbP9LA/bGIa/+nprSe+9LI4gzVPDbrJg+P4fprLFTALMm7+LSb4d+kpdzt/7b7wrQM498cqBzSpr8g/FSh+bzQygL9nSm7qSmM4epQ4flY/BQdqA+l4oYQ2BpAPp87arS34nMQyF8E8nkdqMD6pMzd8/4SL7bF8aRr+7+rG7mkqBpD8pSUzozQcA8Szb87PDSb/d+/qgzVJfl/4LExpdzQ4fRSy7bFP9+y+7+nJAzdaLp/2LSiz/Qz8dbMagYiJdbCwB4QyFSfJ7b7yFSenS4oJA+A8BlO8p8c4A+Q4DbSPB8d8nz/zBEQye4A2BrF/g4M4epQzLTApBRm8nz+a7PApd4C8n8d8Lzl4opQ2BSTGSpDq9zM4rpAq94SngbFJFS9yLRQc7rlq7pFqrQn4FRd+AYS49+N8pP7+npLpd4CanSO8/ZEcnLAp9laanYD8p+V+dP9JMzVanW9q9zl4AmQznQnwopFPd4c4e+Q2BpApDDROaHVHdWEH0iTP0ZMPeqI+0Z9wsIj2erIH0iINsQhP/rjwjQ1J7QTGnIjNsQhP/HjwjHl+AqM+0HEPeLEPAZ7wAr7+AcFP0qI+AcIPePjKc==",
            "x-t": "1775629059902",
            "x-xray-traceid": "ceb5dea37ee3f2842e73479f645a6f9c",
        }
        cookies = {
            "abRequestId": "06b73935-c0f6-53d1-8c4b-f99e90358eed",
            "xsecappid": "xhs-pc-web",
            "a1": "199ce8e93b2kr36a9orz18xi4x3w8hf0ccow6h9kz50000398176",
            "webId": "9642ef0f0e0c4920f51ee088cc7657c7",
            "gid": "yjjSdYdfSdSWyjjSdYdjqSxjDJTFqK0jlFuylTuYC34CqE28EYxi8K888qjYyWK8448fJSSK",
            "ets": "1775564252728",
            "webBuild": "6.4.1",
            "id_token": "VjEAAABVa4IFmiGt1nmJvG2gBMbcBEvhetKwEAHi7AYQjSVi1Rz9Zn72H0ycij3YvlVgF5gO2mv/eHoOWWJhb1owDG5pygQPbJWfZfCKNi19gkz0hjRl6faHQ3zotZxZL3rxMdTq",
            "websectiga": "10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467",
            "sec_poison_id": "54857159-1cf0-470a-b30c-478cd4d93ce9",
            "acw_tc": "0ad6fbdf17756289661933167e6c52cc9f6b4d9d4c8d66491da073b380747a",
            "web_session": web_session,
            "unread": "{%22ub%22:%2269d29526000000001d01df6b%22%2C%22ue%22:%2269d3b6490000000023004a71%22%2C%22uc%22:40}",
            "loadts": "1775629058366",
        }
        url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
        params = {
            "note_id": "69d1e6b2000000001a0268a3",
            "cursor": "",
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": "ABFxNIbwwFRYvbTMW29dEkEf3rAXRnNPa9oZmoxz0Eoiw=",
        }
        try:
            r = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
            ok = r.status_code == 200 and '"code":0' in r.text
            self.log.info(f"API 校验: status={r.status_code} → {'通过' if ok else '失败'}")
            return ok
        except Exception as e:
            self.log.warning(f"API 校验异常: {e}")
            return False

    def close(self):
        try:
            self.page.quit()
        except Exception:
            pass
