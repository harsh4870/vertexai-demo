import re
import time
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
from playwright.sync_api import sync_playwright

INPUT_XLSX = "./Input/Input.xlsx"
SHEET = "h&m"
OUTPUT_CSV = "./Output/h&m.csv"
IMAGE_ROOT = Path("Output/Image")

CARD = ".ds-sdk-product-item"
TITLE = "h2 > a"
PICTURE = ".swiper-slide-active img"


def safe_name(text):
    return re.sub(r'[\\/:*?"<>|]', "-", text)


def grab_cards(page, job):
    folder = IMAGE_ROOT / job["Type"]
    folder.mkdir(parents=True, exist_ok=True)
    rows = []

    for n, card in enumerate(page.query_selector_all(CARD), start=1):
        title_el = card.query_selector(TITLE)
        pic_el = card.query_selector(PICTURE)
        title = title_el.text_content().strip() if title_el else "No title"
        src = pic_el.get_attribute("data-src") if pic_el else None
        if not src:
            print(f"  skip #{n} ({title}): no image")
            continue

        stem = f"{n} {safe_name(title)}"
        urlretrieve(src, folder / f"{stem}.png")
        print(f"  saved {stem}")
        rows.append({
            "Gender": job["Gender"],
            "ItemType": job["Type"],
            "ItemTitle": title,
            "ImageName": stem,
            "ImageURL": src,
        })
    return rows


def run(jobs, show_browser=True):
    collected = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not show_browser, slow_mo=50)
        page = browser.new_page()
        for _, job in jobs.iterrows():
            print(f"Opening {job['URL']}")
            page.goto(job["URL"], timeout=60_000)
            time.sleep(5)
            collected += grab_cards(page, job)
        browser.close()

    pd.DataFrame(collected).to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(collected)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    sheet = pd.read_excel(INPUT_XLSX, sheet_name=SHEET)
    run(sheet[sheet["Status"] == "Yes"])
