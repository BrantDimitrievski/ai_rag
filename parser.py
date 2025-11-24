import os, json
import requests
import unstructured_client
from unstructured_client.models import operations, shared

UNSTRUCTURED_API = os.getenv["UNSTRUCTURED_API_KEY"]

client = unstructured_client.UnstructuredClient(
    api_key_auth= UNSTRUCTURED_API
    # https://platform.unstructuredapp.io/api/v1
)

filename = "PATH_TO_INPUT_FILE"

req = operations.PartitionRequest(
    partition_parameters=shared.PartitionParameters(
        files=shared.Files(
            content=open(filename, "rb"),
            file_name=filename,
        ),
    ),
)