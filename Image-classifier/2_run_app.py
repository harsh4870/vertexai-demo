import io
import os

import streamlit as st
from PIL import Image, ImageDraw

from Library.vertex_ai_predict_image import detect_objects

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "test-x-394811")
REGION = os.getenv("GCP_REGION", "us-central1")
ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID", "4373703873420853248")
KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./auth_gcp_2.json")
SAMPLE_IMAGE = "./Output/Image/Blazer/1 Jaket pendek.png"
UPLOAD_LIMIT_BYTES = 5 * 1024 * 1024
MIN_CONFIDENCE = 0.08

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE

st.set_page_config(layout="wide", page_title="Image Classifier")
st.title("What fashion item is this?")
st.caption("Upload a photo and the Vertex AI model will box the item and name it.")
st.sidebar.header("Your image")

left, right = st.columns(2)
uploaded = st.sidebar.file_uploader("Pick a picture", type=["png", "jpg", "jpeg"])


def to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format=img.format or "PNG")
    return buf.getvalue()


def show_prediction(source):
    photo = Image.open(source)
    left.subheader("You gave us")
    left.image(photo)

    found = detect_objects(
        project=PROJECT_ID,
        endpoint_id=ENDPOINT_ID,
        image_bytes=to_bytes(photo),
        location=REGION,
        min_confidence=MIN_CONFIDENCE,
    )

    if not found or not found["displayNames"]:
        right.error("Model found nothing it recognises.")
        right.image(photo)
        return

    label, score = found["displayNames"][0], found["confidences"][0]
    x0, x1, y0, y1 = found["bboxes"][0]  # normalised 0..1, x pair then y pair
    w, h = photo.size

    boxed = photo.convert("RGB")
    ImageDraw.Draw(boxed).rectangle([x0 * w, y0 * h, x1 * w, y1 * h], outline="red", width=3)

    right.success(f"Looks like a **{label}** ({score:.0%} sure)")
    right.image(boxed)


if uploaded is None:
    show_prediction(SAMPLE_IMAGE)
elif uploaded.size > UPLOAD_LIMIT_BYTES:
    st.error("That file is over 5 MB. Try a smaller one.")
else:
    show_prediction(uploaded)
