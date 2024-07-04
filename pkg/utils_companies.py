from typing import Dict, Union, List
from collections import defaultdict, Counter
from pathlib import Path
import json
import spacy


def write_to_file(data: Dict, file_path: Union[Path, str]) -> None:
    with open(file_path, "w") as f:
        f.writelines(json.dumps(data, indent=4))



def read_json_file(path):
    data = None
    try:
        with open(path, "r") as reader:
            data = json.loads(reader.read())
            return data
    except FileNotFoundError:
        print(f"{path} File Not Found")
    except:
        print(f"Error Reading the FIle {path}")


