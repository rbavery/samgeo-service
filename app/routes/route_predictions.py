import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.get("/predictions", response_class=JSONResponse)
def list_files_in_project(project_id: str = ""):
    public_dir = Path("public").resolve() / Path(project_id)
    if not str(public_dir).startswith(str(Path("public").resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not public_dir.exists() or not public_dir.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")

    files = [f for f in public_dir.iterdir() if f.suffix == ".json"]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    detections = {}

    for file in files:
        if file.is_file():
            base_name, ext = os.path.splitext(file.name)
            if base_name not in detections:
                detections[base_name] = {
                    "geojson_files": [],
                    "id": base_name,
                    "bbox": None,
                    "zoom": None,
                    "image_url": None,
                    "tif_url": None,
                }
            detections[base_name]["geojson_files"] = [
                f"{BASE_URL}/files/{project_id}/{f.name}"
                for f in public_dir.iterdir()
                if f.suffix == ".geojson" and base_name in f.stem
            ]
            if ext == ".json":
                try:
                    with open(file, "r") as json_file:
                        json_content = json.load(json_file)
                        detections[base_name]["bbox"] = json_content.get("bbox", [])
                        detections[base_name]["zoom"] = json_content.get("zoom", None)
                        detections[base_name]["image_url"] = json_content.get("image_url", None)
                        detections[base_name]["tif_url"] = json_content.get("tif_url", None)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Error reading JSON file: {str(e)}"
                    )

    response_data = {"project_id": project_id or "/", "detection": detections}

    return JSONResponse(content=response_data)