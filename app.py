"""獨立唯讀展示入口：只讀已發布的市場研究摘要，不註冊私人研究頁。"""
import json
import re
import hashlib
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent / "public_data"


def published():
    folder = ROOT
    active = ROOT / "active.json"
    if active.exists():
        pointer = json.loads(active.read_text(encoding="utf-8"))
        if not re.fullmatch(r"[a-f0-9]{32}",pointer["generation"]):
            raise ValueError("發布版本格式錯誤。")
        folder = ROOT/"generations"/pointer["generation"]
        hashes = json.loads((folder/"integrity.json").read_text(encoding="utf-8"))
        for name, expected in hashes.items():
            if Path(name).name!=name or hashlib.sha256((folder/name).read_bytes()).hexdigest()!=expected:
                raise ValueError("公開摘要完整性核對失敗。")
    catalog = folder/"catalog.json"
    return folder, json.loads(catalog.read_text(encoding="utf-8")) if catalog.exists() else []


def render():
    st.set_page_config(page_title="股票研究唯讀展示", page_icon="🔬", layout="wide")
    st.title("唯讀研究展示")
    st.info("只呈現已發布歷史研究；私人筆記、核對與封存操作不在這個入口。")
    st.warning("未校準分數不是可靠獲利機率；日線快照不是即時報價。")
    try:
        folder, records = published()
    except (OSError,ValueError,KeyError):
        st.error("摘要讀取或完整性檢查失敗，請由管理者重新發布；不顯示替代結果。")
        return
    update = ROOT/"update.json"
    if update.exists():
        state = json.loads(update.read_text(encoding="utf-8"))
        st.caption(f"最近更新：{state['state']}｜嘗試時間 UTC：{state['attempt_at_utc']}")
        if state['state'] != "SUCCESS":
            st.warning("摘要更新尚未成功確認；畫面依目前有效發布指標讀取，請留意資料日期與發布時間。")
    active = ROOT/'active.json'
    if active.exists():
        pointer = json.loads(active.read_text(encoding='utf-8'))
        st.caption(f"摘要發布時間 UTC：{pointer.get('published_at_utc','未記錄')}。此為歷史研究重算，非即時報價或當日向前預測。")
    if not records:
        st.write("尚無發布摘要。")
        return
    labels = {f"{r['symbol']}｜{r['model']}｜資料截至 {r['data_date']}": r for r in records}
    choice = st.selectbox("研究摘要", list(labels))
    record = labels[choice]
    st.write(f"**行情截至 {record['data_date']}｜訊號日期 {record.get('signal_date',record['data_date'])}**")
    st.caption(f"共同答案已揭曉截至 {record['score_last']}")
    local = pd.Timestamp.now(tz="Asia/Taipei")
    expected = None
    calendar_path = folder/'calendar.json'
    if calendar_path.exists() and record['symbol'].endswith('.TW'):
        schedule = json.loads(calendar_path.read_text(encoding='utf-8'))
        days = pd.DatetimeIndex(schedule['years'].get(str(local.year),[]))
        today = local.normalize().tz_localize(None)
        days = days[days<=today] if local.hour>=16 else days[days<today]
        expected = str(days[-1].date()) if len(days) else None
    st.caption("日線符合最近預定已完成交易日；並非即時報價，臨時休市仍須核對。" if record['data_date']==expected
               else f"保存日線可能過期或未完成；預定已完成日 {expected or '日曆不足'}。未連接即時行情，不判定盤中觸發。")
    if record.get('calendar_gap_n'):
        dates=', '.join(row['date'] for row in record.get('calendar_gaps',[]))
        st.warning(f"資料／日曆缺口 {record['calendar_gap_n']} 筆：{dates or '詳見來源核對'}。歷史報酬按來源有效日計算，實際成交期間仍待確認，不判定進場觸發。")
    st.caption(f"下載時間 UTC：{record.get('fetched_at_utc','舊摘要未記錄')}｜研究產生時間 UTC：{record.get('generated_at_utc','舊摘要未記錄')}")
    key = record["key"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", key):
        st.error("發布索引格式不符。")
        return
    st.caption(f"來源：Yahoo Finance 保存快照｜版本 {record['version']}｜測試訊號共同日期 {record['score_first']}～{record['score_last']}")
    summary = pd.read_csv(folder / f"{key}_summary.csv")
    st.subheader("歷史研究結論")
    for _, row in summary.iterrows():
        st.write(f"**{int(row.horizon)} 日：{row['state']}**｜未校準分數 {row.latest_raw_score:.3f}")
        st.caption(f"相近訊號 {int(row.matched_n)} 筆；{row['reason']}")
    # 公開入口先呈現文字結論。只有使用者展開才傳送完整圖表／grid，避免網路慢時阻擋摘要。
    if st.toggle("顯示完整證據表與回測圖", value=False):
        st.dataframe(summary, width="stretch")
        st.line_chart(pd.read_csv(folder / f"{key}_equity.csv", index_col=0, parse_dates=True), width="stretch")
        st.dataframe(pd.read_csv(folder / f"{key}_metrics.csv"), width="stretch")
    st.caption("簡化對稱成本、分數報酬指數單位。跨期間／模型多重比較未校正；完整交易與期末截尾另列。")


# 明確的單頁登錄會停用同目錄 pages 的自動發現，私人頁不屬於這個服務。
st.navigation([st.Page(render, title="唯讀研究展示", default=True)]).run()
