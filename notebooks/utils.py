from typing import Dict, Union, List
from pathlib import Path
import json
from tqdm import tqdm

def write_to_file(data: Dict, file_path: Union[Path, str]) -> None:
    with open(file_path, "w") as f:
        f.writelines(json.dumps(data))


def read_json_file(path):
    data = None
    try:
        with open(path, "r") as reader:
            data = json.loads(reader.read())
    except FileNotFoundError:
        print(f"{path} File Not Found")
    except: 
        print(f"Error Reading the FIle {path}")

    return data


def get_text_from_reviews(reviews):

    texts = []
    for item in reviews["rows"]:
        texts.append(item["text"])

    return texts


def get_all_text(data):
    reviews_text = []
    for item in tqdm(data):
        reviews_text += get_text_from_reviews(item["reviews"])
    return reviews_text


