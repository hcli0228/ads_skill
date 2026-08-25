import pytest
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ads_api import ADS

@pytest.fixture(scope="session")
def ads():
    return ADS()

def test_library_crud_lifecycle(ads):
    lib_name = f"TestLib_{uuid.uuid4().hex[:8]}"
    
    # 1. Create library
    created = ads.libraries.create_library(
        name=lib_name,
        description="Automated Test Library",
        public=False,
        bibcodes=["1975CMaPh..43..199H"]
    )
    assert "id" in created or "library_id" in created or "name" in created
    lib_id = created.get("id") or created.get("library_id")
    
    try:
        # 2. List libraries
        libs = ads.libraries.list_libraries()
        lib_ids = [l.get("id") for l in libs]
        assert lib_id in lib_ids

        # 3. Add document
        add_res = ads.libraries.add_documents(lib_id, ["1974Natur.248...30H"])
        assert add_res is not None

        # 4. Get library contents
        lib_detail = ads.libraries.get_library(lib_id)
        docs = lib_detail.get("documents", [])
        assert "1975CMaPh..43..199H" in docs or "1974Natur.248...30H" in docs

        # 5. Remove document
        ads.libraries.remove_documents(lib_id, ["1974Natur.248...30H"])

    finally:
        # 6. Delete library (cleanup)
        ads.libraries.delete_library(lib_id)
