# Task

前往臺灣銀行牌告匯率官網，查詢並回報最新的美金現鈔買入與賣出匯率

# Critical Points
- [x] CP1: Navigate to 臺灣銀行牌告匯率官網 (https://rate.bot.com.tw/xrt?Lang=zh-TW) — log line 1, screenshot 1
- [x] CP2: Locate the row for 美金 (USD) in the exchange rate table — log line 2, screenshot 2
- [x] CP3: Extract 現金買入 (Cash Buying) rate for USD — log line 3 = 31.625, screenshot 3
- [x] CP4: Extract 現金賣出 (Cash Selling) rate for USD — log line 4 = 32.295, screenshot 4
- [x] CP5: Record both rates as the final datum in the log — FINAL_RESPONSE line
