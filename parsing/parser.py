import os, json
import unstructured_client
from unstructured_client.models import operations, shared
from pathlib import Path
import parsing.helper as helper
import jsondb.database as db
from dotenv import load_dotenv

load_dotenv()
UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")

if not UNSTRUCTURED_API_KEY:
    raise RuntimeError("UNSTRUCTURED_API_KEY is not set; unable to call Unstructured API.")

client = unstructured_client.UnstructuredClient(
    api_key_auth=UNSTRUCTURED_API_KEY,
    # server_url = "https://platform.unstructuredapp.io/api/v1"
)


def parse_docs(file_path: Path) -> list[dict]:
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        partition_params = shared.PartitionParameters(
            files=shared.Files(
                content=file_bytes,
                file_name=file_path.name,
            ),
            strategy=shared.Strategy.AUTO,
            languages=["eng", "fra"],
        )

        req = operations.PartitionRequest(
            partition_parameters=partition_params,
        )

        res = client.general.partition(request=req)

    except Exception as e:
        print(f"[ERROR] Unstructured failed for {file_path}: {e}")
        return []

    elements = getattr(res, "elements", None)
    if not elements:
        print(f"Nothing parsed for {file_path}")
        return []

    element_dicts = [
        el if isinstance(el, dict) else el.to_dict()
        for el in elements
    ]

    return element_dicts


def process_single_file(path: Path, db_path: str = "parsed_docs.db") -> None:
    try:
        elements = parse_docs(path)
        if not elements:
            return

        full_text = helper.get_full_text(elements)
        title = helper.get_title(elements, fallback=path.name)
        domain_tags = helper.detect_domain(full_text)
        doc_type = helper.detect_doc_type(full_text, path)
        year = helper.detect_year(full_text)

        db.insert_doc(
            file_path=str(path),
            title=title,
            domain=domain_tags,
            doc_type=doc_type,
            year=year,
            json_data=elements,
            db_path=db_path,
        )

        print(
            f"[OK] Inserted: {path} | "
            f"title='{title}' | domain={domain_tags} | doc_type={doc_type} | year={year}"
        )
    except Exception as e:
        print(f"[ERROR] Unexpected failure for {path}: {e}")


def process_workspace(workspace_dir: str = "workspace", db_path: str = "parsed_docs.db") -> None:
    workspace_path = Path(workspace_dir)

    if not workspace_path.exists():
        print(f"[WARN] Workspace directory not found: {workspace_path}")
        return

    db.init_db(db_path)

    for path in workspace_path.iterdir():
        if path.is_file():
            # check for file ext?
            process_single_file(path, db_path=db_path)

    print("Parsing complete. Docs have been stored in the database.")


if __name__ == "__main__":
    process_workspace("workspace", db_path="parsed_docs.db")
