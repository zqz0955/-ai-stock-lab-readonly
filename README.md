# AI 股票研究實驗室：唯讀展示

這個目錄可獨立部署，只呈現已發布的台股歷史研究摘要。它不包含私人筆記、核對操作、封存、原始行情、訓練入口或API key。

模型分數未校準，歷史回測不代表向前有效；資料不足時保持「尚無足夠買入依據」。日線快照不是即時報價，資料日期與交易日曆缺口另列。

## 免費 Community Cloud 設定

1. 將此目錄的內容放到獨立GitHub儲存庫根目錄，保留public_data子目錄。
2. 在Streamlit Community Cloud使用GitHub登入，選此儲存庫、main分支、app.py。
3. Python選3.12；requirements.txt已固定Streamlit與pandas版本。本入口不需要Secrets。
4. 選可用的streamlit.app子網域後部署，重新驗證HTTPS、資料日期、websocket、刷新與手機操作。

唯讀入口可在雲端呈現保存摘要，不需要原研究電腦一直開機；**新摘要產生與發布仍需要研究環境完成更新並提交這個儲存庫**。Community Cloud不會自行下載行情或重新訓練。未更新時畫面顯示過期／來源缺口。

固定入口：[開啟唯讀研究展示](https://zqz0955--ai-stock-lab-readonly-app-x1owmm.streamlit.app/)。已驗證公開HTTPS、摘要、圖表、重新整理、三個同時使用的獨立瀏覽器session及390px手機尺寸；尚未用實體手機或行動網路驗證。這是免費教學展示，不代表持續可用性保證。

目前發布資料截至2026-10-07，模型仍未校準，存在來源／日曆缺口；以畫面列出的日期與缺口為準。**目前沒有自動提交新摘要至GitHub的流程**，本機更新完成不代表雲端已更新。

此方案已由使用者選擇，不訂閱付費服務。官方：[Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)、[部署設定](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)。

## 本機查看

```text
python -m pip install -r requirements.txt
streamlit run app.py --server.port=8504
```

public_data/active.json選擇一次完整發布，對應generation內的檔案以SHA256核對。若更新失敗，保留上一份成功摘要。不能把更新SUCCESS當行情完整性或模型有效性證明。

本地Dockerfile為可審查範本，尚未在目前Windows環境實測。不要把完整私人研究專案或金鑰加到這個目錄。
