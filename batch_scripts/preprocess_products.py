import argparse
import json
import os
import uuid
from pathlib import Path
from typing import List, Optional
from types import SimpleNamespace
from PIL import Image

try:
    from backend.src.backend_base_services import upload_product_service
except ModuleNotFoundError:
    import sys
    def _find_repo_root(max_levels: int = 6) -> Path:
        p = Path(__file__).resolve()
        for i in range(1, max_levels):
            try:
                candidate = p.parents[i]
            except IndexError:
                break
            if (candidate / "backend").exists():
                return candidate
        return p.parents[1]

    repo_root = _find_repo_root()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from backend.src.backend_base_services import upload_product_service

PRODUCT_CATEGORIES = [
    "fashion",
    "beauty",
    "electronics",
    "home",
    "fitness",
    "food",
    "baby",
    "automotive",
    "pets",
    "gaming",
]

def list_json_files(folder: str) -> List[str]:
    p = Path(folder)
    if not p.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    return [str(f) for f in p.iterdir() if f.is_file() and f.suffix.lower() == ".json"]

def detect_category(item_keywords, categories=PRODUCT_CATEGORIES) -> Optional[str]:
    """Return a matching category string or None if no category matches."""
    if item_keywords is None:
        return None

    # Normalize keywords into single lowercase string for searching
    if isinstance(item_keywords, list):
        kw_text = " ".join([str(x) for x in item_keywords]).lower()
    else:
        kw_text = str(item_keywords).lower()

    for cat in categories:
        if cat in kw_text:
            return cat

    return None

class _CategoryObj:
    def __init__(self, value: str):
        self.value = value

class _RequestPayload:
    def __init__(self, title: str, description: str, category_value: str):
        self.title = title
        self.description = description
        self.category = _CategoryObj(category_value)

def process_product_entry(product: dict, json_path: str, image_base_folder: str, idx: int, debug: bool = False) -> Optional[dict]:
    # Extract expected fields (fall back to sensible defaults)
    def _first_value_from_field(field):
        v = product.get(field)
        if v is None:
            return None
        # If it's a list of language dicts like [{'language_tag':..., 'value': '...'}]
        if isinstance(v, list) and len(v) > 0:
            first = v[0]
            if isinstance(first, dict) and "value" in first:
                return str(first["value"])
            if isinstance(first, str):
                return first
            return str(first)
        # If it's a dict with 'value'
        if isinstance(v, dict) and "value" in v:
            return str(v["value"])
        # Otherwise stringify
        return str(v)

    item_name = _first_value_from_field("item_name") or _first_value_from_field("title") or f"product-{idx}"
    item_keywords = product.get("item_keywords")

    product_description = _first_value_from_field("product_description") or _first_value_from_field("description") or ""
    main_image_rel = product.get("main_image_path")

    if not main_image_rel:
        if debug:
            print(f"Skipping product #{idx} in {json_path}: no main_image_path present")
        return None

    image_path = os.path.join(image_base_folder, main_image_rel)
    if not os.path.exists(image_path):
        if debug:
            print(f"Image not found for product #{idx} in {json_path}: {image_path}")
        return None

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        if debug:
            print(f"Failed to open image {image_path} for product #{idx}: {e}")
        return None

    # Determine category; discard if no match
    category = detect_category(item_keywords)
    if category is None:
        if debug:
            print(f"Discarding product {item_name} (no matching category)")
            print()
        return None

    req = _RequestPayload(title=item_name, description=product_description, category_value=category)
    product_id = str(uuid.uuid4())

    try:
        result = upload_product_service(product_id, img, req)
        if debug:
            print(f"Uploaded product {product_id}: {result}")
            print()
        # Return the category string on success so callers can tally counts
        return category
    except Exception as e:
        if debug:
            print(f"Failed to upload product {product_id}: {e}")
        return None

def process_products_in_file(json_path: str, image_base_folder: str, debug: bool = False, category_counts: Optional[dict] = None) -> int:
    """Load a JSON file that may contain many product entries and process them.

    Returns the number of products processed (successes + skips).
    """
    items = None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if "products" in data and isinstance(data["products"], list):
                items = data["products"]
            else:
                vals = [v for v in data.values() if isinstance(v, dict)]
                items = vals if vals else [data]
        else:
            if debug:
                print(f"Unrecognized JSON structure in {json_path}, skipping")
            return 0
    except Exception:
        items = []
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        items.append(obj)
                    except Exception as e:
                        if debug:
                            print(f"Skipping invalid JSON on line {line_no+1} in {json_path}: {e}")
                        continue
        except Exception as e:
            if debug:
                print(f"Failed to read {json_path} as NDJSON: {e}")
            return 0

    count = 0
    for idx, product in enumerate(items):
        try:
            # Pre-check category to enforce per-category cap when debug is enabled
            pre_cat = detect_category(product.get("item_keywords"))
            if pre_cat is None:
                # Let process_product_entry handle messaging for missing category
                res = process_product_entry(product, json_path, image_base_folder, idx, debug=debug)
                if res is not None and category_counts is not None:
                    category_counts[res] = category_counts.get(res, 0) + 1
            else:
                if debug and category_counts is not None and category_counts.get(pre_cat, 0) >= 25:
                    if debug:
                        print(f"Skipping product #{idx} in {json_path}: category '{pre_cat}' reached 25-item cap")
                else:
                    res = process_product_entry(product, json_path, image_base_folder, idx, debug=debug)
                    if res is not None and category_counts is not None:
                        category_counts[res] = category_counts.get(res, 0) + 1
        except Exception as e:
            if debug:
                print(f"Unexpected failure processing entry #{idx} in {json_path}: {e}")
        count += 1

        # Print progress periodically for large files
        if debug and (idx + 1) % 100 == 0:
            print(f"Processed {idx+1} products from {json_path}")

    return count

def classify_products_in_folder(json_folder: str, image_base_folder: str, debug: bool = False) -> None:
    files = list_json_files(json_folder)
    if not files:
        print(f"No json files found in {json_folder}")
        return
    total = 0
    category_counts = {}
    for json_path in files:
        try:
            processed = process_products_in_file(json_path, image_base_folder, debug=debug, category_counts=category_counts)
            total += processed
            if debug:
                print(f"Finished {json_path}: {processed} entries processed")
        except Exception as e:
            if debug:
                print(f"Unexpected failure processing {json_path}: {e}")

    if debug:
        print(f"Total product entries processed: {total}")
        print("Products added per category:")
        for cat, cnt in sorted(category_counts.items(), key=lambda x: x[0]):
            print(f"  {cat}: {cnt}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_folder", help="Path to folder containing product .json files")
    parser.add_argument("--image_base_folder", help="Parent folder for product images referenced by main_image_path")
    parser.add_argument("--debug", action="store_true", help="Enable debug printing")
    args = parser.parse_args()

    classify_products_in_folder(args.json_folder, args.image_base_folder, debug=args.debug)

if __name__ == "__main__":
    main()
