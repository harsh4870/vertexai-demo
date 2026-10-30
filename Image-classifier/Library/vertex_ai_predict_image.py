import base64

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict


def detect_objects(project, endpoint_id, image_bytes, location="us-central1", min_confidence=0.5, top_n=5):
    client = aiplatform.gapic.PredictionServiceClient(
        client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
    )

    payload = predict.instance.ImageObjectDetectionPredictionInstance(
        content=base64.b64encode(image_bytes).decode("ascii")
    ).to_value()
    options = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=min_confidence,
        max_predictions=top_n,
    ).to_value()

    resource = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
    reply = client.predict(endpoint=resource, instances=[payload], parameters=options)

    # one image in, so at most one prediction comes back
    return dict(reply.predictions[-1]) if reply.predictions else None
