# 👗 Point a Camera at Fashion, Let Google's AI Name It

Upload a photo of a jacket or a dress. A few seconds later a red box lands on the item and a model running on **Google Cloud Vertex AI** tells you what it is, and how sure it is.

That's the whole demo. Behind it sit three small pieces:

```
 H&M website ──► scraper ──► labelled photos ──► Vertex AI trains a model
                                                          │
          you upload a photo ──► Streamlit app ──► model endpoint ──► box + label
```

You can run it on **Windows, macOS or Linux**. Every command below has a tab-free, copy-paste version for each.

---

## What's in the box

Everything lives in the `Image-classifier/` folder:

| Path | What it does |
|---|---|
| `1_image_scrapper.py` | Opens a real browser, visits the product pages listed in `Input/Input.xlsx`, saves every product photo into `Output/Image/<Type>/` and writes a CSV summary |
| `2_run_app.py` | The Streamlit web app students will actually see |
| `Library/vertex_ai_predict_image.py` | One function that sends an image to your Vertex AI endpoint and returns the detections |
| `Input/Input.xlsx` | The shopping list: which URLs to scrape (`URL`, `Type`, `Gender`, `Status` columns) |
| `Output/` | Scraped images and the CSV. Created for you |
| `auth_gcp_*.json` | Your Google service-account key goes here (not in the repo). **Secret. See the warning below** |

---

## Before you start

You need:

1. **Python 3.9 or newer.** Check with the command for your system:

   ```bash
   python3 --version      # macOS / Linux
   ```
   ```powershell
   python --version       # Windows
   ```
   Not installed? Grab it from [python.org](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** in the installer or nothing below will work.

2. **A Google Cloud project** with Vertex AI switched on and a trained **image object detection** model deployed to an endpoint. You need three facts from it: *project ID*, *region*, *endpoint ID*.

3. **A service-account key (JSON)** that is allowed to call Vertex AI (role: *Vertex AI User*).

> ⚠️ **Never commit or share the key file.** Anyone holding it can spend your cloud money. The included `.gitignore` already blocks `auth_gcp_*.json`. If a key ever lands in a public repo, delete it in the Google Cloud console right away and make a new one.

---

## Step 1: Get set up

Grab the code and step into the app folder (same on every system):

```bash
git clone https://github.com/harsh4870/vertexai-demo.git
cd vertexai-demo/Image-classifier
```

No git? Hit the green **Code → Download ZIP** button on GitHub, unzip, and open a terminal inside the `Image-classifier` folder.

Then pick your system. Every command from here on runs inside `Image-classifier`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### Windows (Command Prompt)

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
playwright install chromium
```

> 💡 **PowerShell says "running scripts is disabled"?** Run this once, then retry the activate line:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

You'll know the virtual environment is on when `(.venv)` shows up at the start of your prompt.

---

## Step 2: Tell the app about your Google Cloud

The app reads four settings from environment variables. Anything you skip falls back to the author's demo values, which will **not** work on your account, so set them.

### macOS / Linux

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./auth_gcp_2.json"
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export VERTEX_ENDPOINT_ID="1234567890123456789"
```

### Windows (PowerShell)

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\auth_gcp_2.json"
$env:GCP_PROJECT_ID = "your-project-id"
$env:GCP_REGION = "us-central1"
$env:VERTEX_ENDPOINT_ID = "1234567890123456789"
```

### Windows (Command Prompt)

```bat
set GOOGLE_APPLICATION_CREDENTIALS=.\auth_gcp_2.json
set GCP_PROJECT_ID=your-project-id
set GCP_REGION=us-central1
set VERTEX_ENDPOINT_ID=1234567890123456789
```

These last only for the current terminal window. Close it and you'll need to set them again.

---

## Step 3: Run the app 🚀

Same command on every system:

```bash
streamlit run 2_run_app.py
```

Your browser opens at `http://localhost:8501`. Here's what to try on stage:

1. Leave it alone first. It loads a sample blazer by itself, so the audience sees a result instantly.
2. Upload your own picture from the sidebar (PNG or JPG, under 5 MB).
3. Watch the left side (your photo) and the right side (the same photo with the red box and label).
4. Upload something that isn't clothing, like a mug. Showing the model say *"found nothing it recognises"* is a great moment to explain confidence thresholds.

---

## Step 4 (optional): Collect your own training photos

This is where the dataset came from. It drives a real Chromium window so you can watch it work.

1. Open `Input/Input.xlsx`, sheet `h&m`.
2. Each row is a page to visit. Set `Status` to `Yes` for the rows you want, anything else is skipped.
3. Run:

   ```bash
   python 1_image_scrapper.py
   ```

   (On Windows use `python` instead of `python3` if the first one isn't recognised.)

Photos land in `Output/Image/Blazer/`, `Output/Image/Dress/` and so on, one folder per `Type`. A summary goes to `Output/h&m.csv`.

> 🧭 **Be a good web citizen.** Scrape only for learning, keep the pause between pages, and check a site's terms before pointing this at anything else. Shop pages also change their HTML now and then. If the scraper returns zero items, the CSS selectors at the top of `1_image_scrapper.py` (`CARD`, `TITLE`, `PICTURE`) are what to update.

From here the workflow in Google Cloud is: upload the folders to a bucket, draw boxes on them in a Vertex AI dataset, train an *image object detection* model, deploy it to an endpoint. That endpoint ID is what you set in Step 2.

---

## How the pieces talk (for the curious student in row three)

When you upload a picture, the app:

1. Converts it to bytes and base64-encodes it.
2. Sends it to your endpoint with `PredictionServiceClient.predict`, asking for at most 5 detections above a confidence of 0.08.
3. Takes the best detection. Boxes come back as fractions between 0 and 1 in the order *x-min, x-max, y-min, y-max*, so the app multiplies by the image width and height to get real pixels.
4. Draws the rectangle with Pillow and shows the label.

The whole cloud call is about 15 lines in `Library/vertex_ai_predict_image.py`. Open it live. It's short enough to read in front of a class.

---

## When things go wrong

| You see | Likely reason | Fix |
|---|---|---|
| `command not found: streamlit` / `'streamlit' is not recognized` | Virtual environment not active | Run the activate line from Step 1 again |
| `DefaultCredentialsError` or `File ... was not found` | Wrong path to the key file | Check `GOOGLE_APPLICATION_CREDENTIALS` and that you're in the project folder |
| `403 Permission denied` | Service account lacks the role | Give it **Vertex AI User** in IAM |
| `404 ... endpoint not found` | Wrong endpoint ID, project or region | Copy all three again from the Vertex AI console |
| App always says "nothing it recognises" | Confidence too strict, or the photo is very different from training data | Lower `MIN_CONFIDENCE` in `2_run_app.py`, or try a cleaner product-style picture |
| Playwright complains about a missing browser | Browsers weren't downloaded | `playwright install chromium` |
| `Address already in use` | Another Streamlit is running | `streamlit run 2_run_app.py --server.port 8502` |

---

## 💸 A word on cost

A deployed Vertex AI endpoint **bills per hour while it's up**, whether anyone is using it or not. After the demo, go to *Vertex AI → Online prediction → Endpoints*, undeploy the model, and delete the endpoint if you're done with it. Do this before you close the laptop, not after.

---

## Ideas to hand the class as homework

- Add a second detection and draw all boxes, not just the best one.
- Show the confidence as a progress bar.
- Scrape a different category and retrain.
- Swap the cloud call for a local model and compare speed.
