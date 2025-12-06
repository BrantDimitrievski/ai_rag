import os, json
import unstructured_client
from unstructured_client.models import operations, shared
from pathlib import Path

UNSTRUCTURED_API = os.getenv["UNSTRUCTURED_API_KEY"]

client = unstructured_client.UnstructuredClient(
    api_key_auth= UNSTRUCTURED_API
    # server_url= "https://platform.unstructuredapp.io/api/v1"
)

