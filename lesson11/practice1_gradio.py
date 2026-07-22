from datetime import datetime
from pathlib import Path

import gradio as gr
from gradio.themes import Soft
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

# 截圖存放資料夾
SHOT_DIR = Path(__file__).parent / "shots"
SHOT_DIR.mkdir(exist_ok=True)


def launch_browser(p: Playwright) -> Browser:
  """啟動 Chromium 瀏覽器實例"""
  return p.chromium.launch()


def search_wikipedia(page: Page, keyword: str) -> str:
  """在維基百科搜尋指定關鍵字，回傳截圖路徑"""
  page.goto("https://zh.wikipedia.org")
  page.locator("#searchInput").fill(keyword)
  shot_path = SHOT_DIR / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
  page.screenshot(path=str(shot_path))
  page.keyboard.press("Enter")
  page.wait_for_load_state("networkidle")
  return str(shot_path)


def get_search_result(page: Page) -> dict[str, str]:
  """擷取搜尋結果頁面的標題與摘要"""
  heading: str = page.locator("#firstHeading").inner_text()
  elements = page.locator("#mw-content-text p")
  content: str = elements.first.inner_text() if elements.count() > 0 else ""
  return {"heading": heading, "content": content.strip()}


def crawl(keyword: str) -> tuple[str, str, str | None]:
  """爬蟲主流程，回傳 (標題, 摘要, 截圖路徑) 供 Gradio 使用"""
  keyword = (keyword or "").strip()
  if not keyword:
    return "⚠️ 請先輸入關鍵字", "", None

  with sync_playwright() as p:
    browser: Browser = launch_browser(p)
    try:
      page: Page = browser.new_page()
      shot_path = search_wikipedia(page, keyword)
      result = get_search_result(page)
      heading = f"📖 {result['heading']}"
      content = result["content"] or "（找不到摘要內容）"
      return heading, content, shot_path
    except Exception as e:
      return "❌ 爬蟲執行失敗", str(e), None
    finally:
      browser.close()


# ---------- Gradio 介面 ----------

CUSTOM_CSS = """
.gradio-container {
  max-width: 960px !important;
  margin: auto !important;
}
#hero {
  text-align: center;
  padding: 28px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  color: #fff;
  box-shadow: 0 10px 30px rgba(99,102,241,.35);
  margin-bottom: 8px;
}
#hero h1 { font-size: 2rem; margin: 0; font-weight: 800; letter-spacing: 1px; }
#hero p  { margin: 6px 0 0; opacity: .92; }
.result-card { border-radius: 14px !important; }
footer { visibility: hidden; }
"""

with gr.Blocks(
  title="維基百科搜尋爬蟲",
  theme=Soft(primary_hue="violet", secondary_hue="pink"),
  css=CUSTOM_CSS,
) as demo:

  gr.HTML(
    """
    <div id="hero">
      <h1>🌐 維基百科搜尋爬蟲</h1>
      <p>輸入關鍵字，使用 Playwright 自動搜尋維基百科並擷取內容與截圖</p>
    </div>
    """
  )

  with gr.Row():
    keyword_box = gr.Textbox(
      label="搜尋關鍵字",
      placeholder="例如：臺灣、Python、人工智慧…",
      scale=4,
      autofocus=True,
    )
    search_btn = gr.Button("🔍 開始搜尋", variant="primary", scale=1)

  gr.Examples(
    examples=["臺灣", "Python", "人工智慧", "台北101", "珍珠奶茶"],
    inputs=keyword_box,
    label="快速範例",
  )

  with gr.Row():
    with gr.Column(scale=1):
      heading_out = gr.Textbox(label="搜尋主題", interactive=False)
      content_out = gr.Textbox(label="摘要內容", lines=10, interactive=False)
    with gr.Column(scale=1):
      shot_out = gr.Image(
        label="搜尋當下截圖",
        type="filepath",
        elem_classes="result-card",
      )

  search_btn.click(
    fn=crawl,
    inputs=keyword_box,
    outputs=[heading_out, content_out, shot_out],
    api_name="crawl",
  )
  keyword_box.submit(
    fn=crawl,
    inputs=keyword_box,
    outputs=[heading_out, content_out, shot_out],
  )


if __name__ == "__main__":
  demo.launch()
