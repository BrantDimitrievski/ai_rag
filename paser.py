import os, json
import unstructured_client
from unstructured_client.models import operations, shared
from pathlib import Path
import helper as helper
import database as db

UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")

client = unstructured_client.UnstructuredClient(
    api_key_auth=UNSTRUCTURED_API_KEY,
    # server_url = "https://platform.unstructuredapp.io/api/v1"
)


def parse_docs(file_path: Path) -> list[dict]:

    req = {
        "partition_parameters": {
            "files": {
                "content": open(file_path, "rb"),
                "file_name": file_path.name,
            },
            "strategy": shared.Strategy.AUTO,
            "languages": ["eng", "fra"],
        }
    }

    try:
        res = client.general.partition(request=req)
    finally:
        req["partition_parameters"]["files"]["content"].close()

    if getattr(res, "elements", None) is None:
        print(f"Nothing was parsed for {file_path}")
        return []

    return res.elements



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


def process_workspace(workspace_dir: str = "workspace", db_path: str = "parsed_docs.db" ) -> None:
    workspace_path = Path(workspace_dir)

    db.init_db(db_path)

    for path in workspace_path:
        process_single_file(path, db_path=db_path)

    print("Parsing Complete. Docs have turned into JSON")


if __name__ == "__main__":
    process_workspace("workspace", db_path="parsed_docs.db")