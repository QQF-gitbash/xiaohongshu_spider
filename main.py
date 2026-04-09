"""入口：搜索关键词 → 收割 (note_id, xsec_token, user_id) → 调评论 API → 存 csv

输出目录: data/{keyword}_{yyyy-mm-dd}/
  - note_id.csv : note_id, xsec_token, user_id
  - note.csv    : note_id, comment_json (评论接口返回的整段 JSON)
"""
import asyncio
import csv
import json
import time
from datetime import datetime
from pathlib import Path

from browser.dp_manager import DPManager
from browser.feed_harvester import FeedHarvester
from spiders.comment_spider import CommentSpider
from config.settings import DATA_DIR




async def main(KEYWORD,MAX_NOTES):
    browser = DPManager(headless=False)

    # 1) 登录
    if not browser.is_logged_in():
        await browser.login()

    web_session = browser.get_cookies().get("web_session", "")
    print(f"使用 web_session = {web_session}")

    # 2) 准备输出目录
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path(DATA_DIR) / f"{KEYWORD}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    note_id_csv = out_dir / "note_id.csv"
    note_csv = out_dir / "note.csv"
    print(f"输出目录: {out_dir}")

    # 3) 收割任务列表
    harvester = FeedHarvester(browser)
    tasks = harvester.harvest_search(KEYWORD, max_notes=MAX_NOTES, scroll_times=5)
    print(f"收割到 {len(tasks)} 个任务")

    # 兜底：收割 0 条 → 大概率撞上登录蒙版 → 强制扫码后重试一次
    if len(tasks) == 0:
        print("⚠ 收割 0 条，疑似登录蒙版拦截，强制扫码后重试")
        browser._verified = False
        await browser.login()
        tasks = harvester.harvest_search(KEYWORD, max_notes=MAX_NOTES, scroll_times=5)
        print(f"重试后收割到 {len(tasks)} 个任务")

    # 4) 写 note_id.csv
    with open(note_id_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["note_id", "xsec_token", "user_id"])
        for t in tasks:
            w.writerow([t["note_id"], t["xsec_token"], t.get("user_id", "")])
    print(f"已写入 {note_id_csv} ({len(tasks)} 行)")


    time.sleep(10)
    print('等待10s冷却')

    # 5) 循环调评论 API → 写 note.csv
    spider = CommentSpider(dp_manager=browser)
    with open(note_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["note_id", "comment_json"])
        for i, t in enumerate(tasks, 1):
            nid, xt = t["note_id"], t["xsec_token"]
            try:
                data = spider.fetch_one(nid, xt)
                w.writerow([nid, json.dumps(data, ensure_ascii=False)])
                print(f"[{i}/{len(tasks)}] {nid} -> {data}")
            except Exception as e:
                w.writerow([nid, f"ERROR: {e}"])
                print(f"[{i}/{len(tasks)}] {nid} 失败: {e}")
            time.sleep(5.0)  # 礼貌间隔
    spider.close()

    print(f"完成 → {note_csv}")
    browser.close()


if __name__ == "__main__":
    asyncio.run(main('美食', 1))
