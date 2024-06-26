from typing import Dict, Union, List
from collections import defaultdict, Counter
from pathlib import Path
import json
import spacy
from tqdm import tqdm


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


def get_text_from_reviews(reviews):

    texts = []
    for item in reviews["rows"]:
        texts.append(item["text"])

    return texts


def get_text_and_rating_from_reviews(reviews):

    text_rating_tuple = []
    for item in reviews["rows"]:
        if item["text"]:
            text_rating_tuple.append((item["text"], item["rating"]))

    return text_rating_tuple


def get_all_text_data(data, rating=False):
    result = []
    process_func = None

    if rating:
        process_func = get_text_and_rating_from_reviews
    else:
        process_func = get_text_from_reviews
    for item in data:
        result += process_func(item["reviews"])

    return result


def get_nouns_by_freq(
    rating_text_dict, nlp, rating_value, top_n_word, top_n_association
):
    texts = rating_text_dict[rating_value]
    docs = [nlp(text) for text in texts]

    word_frequency = defaultdict(int)
    associated_adjectives = defaultdict(list)

    for doc in docs:
        for token in doc:
            if not (token.is_stop or token.is_punct) and token.pos_ == "NOUN":
                word_frequency[token.lemma_] += 1

                for child in token.children:
                    if not (child.is_punct or child.is_stop) and child.pos_ == "ADJ":
                        associated_adjectives[token.lemma_].append(child.lemma_)

    top_n_word = (
        top_n_word if top_n_word <= len(word_frequency) else len(word_frequency)
    )

    word_frequency = dict(
        sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:top_n_word]
    )
    filtered_associations = defaultdict(list)
    for key, value in associated_adjectives.items():
        if key in word_frequency:
            temp_top_n_association = (
                top_n_association
                if top_n_association <= len(associated_adjectives[key])
                else len(associated_adjectives)
            )

            filtered_associations[key] = dict(
                sorted(Counter(value).items(), key=lambda x: x[1], reverse=True)[
                    :temp_top_n_association
                ]
            )

    return word_frequency, filtered_associations


def create_rating_text_dict(data):

    text_rating = get_all_text_data(data, rating=True)
    text, rating = zip(*text_rating)
    rating_text_dict = {key: [] for key in list(["good", "bad"])}

    for text, rating in text_rating:
        key = "good" if rating >= 4 else "bad"
        rating_text_dict[key].append(text)

    return rating_text_dict


def get_refined_data(
    raw_reviews_path,
    output_file_path,
    rating_values=["good", "bad"],
    model="en_core_web_sm",
    top_n_word=25,
    top_n_association=5,
):
    reviews = read_json_file(path=raw_reviews_path)

    rating_text_dict = create_rating_text_dict(reviews["data"])

    nlp = spacy.load(model)
    result = {key: [] for key in list(rating_values)}

    print("processing for classes ['good','bad']")
    for value in tqdm(rating_values):
        word_frequency, associated_adjectives = get_nouns_by_freq(
            rating_text_dict=rating_text_dict,
            nlp=nlp,
            rating_value=value,
            top_n_word=top_n_word,
            top_n_association=top_n_association,
        )
        result[value] = {
            "word_freqs": word_frequency,
            "associated_adjectives": associated_adjectives,
        }

    write_to_file(data=result, file_path=output_file_path)
    print("Writing to output file complete")
