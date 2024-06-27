from typing import Dict, Union, List
from collections import defaultdict, Counter
from pathlib import Path
import json
import spacy
from tqdm import tqdm
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


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


def get_word_groups(words: List[str], nlp, threshold):

    word_vectors = [nlp(word).vector for word in words]

    similarity_matrix = cosine_similarity(word_vectors)
    groups = set()

    for idx1, word in enumerate(words):
        word_group = [word]
        for idx2, cos_value in enumerate(similarity_matrix[idx1]):
            if idx1 != idx2 and cos_value >= threshold:
                word_group.append(words[idx2])

        groups.add(tuple(sorted(word_group)))

    return groups


def get_filtered_word_groups(groups):
    unique_groups = []

    for group in groups:
        is_subset = False

        for other_group in groups:
            if group != other_group:
                if set(group).issubset(set(other_group)):
                    is_subset = True
                    break
        if not is_subset:
            unique_groups.append(list(group))
    return unique_groups


def get_filtered_word_frequency(word_frequency, word_groups):
    filtered_word_frequency = defaultdict(int)
    for group in word_groups:
        key_word = group[0]
        for word in group:
            filtered_word_frequency[key_word] += word_frequency[word]

    return filtered_word_frequency


def get_nouns_by_freq(
    rating_text_dict, nlp, rating_value, top_n_word, top_n_association, threshold
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

    word_groups = get_word_groups(list(word_frequency.keys()), nlp, threshold)

    unique_word_groups = get_filtered_word_groups(word_groups)

    # word_frequency = dict(
    #     sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
    # )

    filtered_word_frequency = get_filtered_word_frequency(
        word_frequency, unique_word_groups
    )

    median_word_frequency = np.percentile(list(word_frequency.values()), top_n_word)

    filtered_word_frequency = {
        key: value
        for key, value in filtered_word_frequency.items()
        if value >= median_word_frequency
    }

    filtered_word_frequency = dict(
        sorted(filtered_word_frequency.items(), key=lambda x: x[1], reverse=True)
    )
    filtered_word_group_dict = create_filtered_word_group_dict(
        unique_word_groups, filtered_word_frequency
    )

    filtered_associations = defaultdict(list)
    for key, value in associated_adjectives.items():
        if key in filtered_word_frequency:
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
    return filtered_word_frequency, filtered_associations, filtered_word_group_dict


def create_filtered_word_group_dict(unique_word_groups, filtered_word_frequency):
    word_group_dict = defaultdict(list)
    for group in unique_word_groups:
        if group[0] in filtered_word_frequency:
            word_group_dict[group[0]] = group
    return word_group_dict


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
    threshold=0.7,
):
    reviews = read_json_file(path=raw_reviews_path)

    rating_text_dict = create_rating_text_dict(reviews["data"])

    nlp = spacy.load(model)
    result = {key: [] for key in list(rating_values)}

    print(f"processing for classes {rating_values}")
    for value in tqdm(rating_values):
        word_frequency, associated_adjectives, word_groups = get_nouns_by_freq(
            rating_text_dict=rating_text_dict,
            nlp=nlp,
            rating_value=value,
            top_n_word=top_n_word,
            top_n_association=top_n_association,
            threshold=threshold,
        )
        result[value] = {
            "word_freqs": word_frequency,
            "associated_adjectives": associated_adjectives,
            "word_groups": word_groups,
        }

    write_to_file(data=result, file_path=output_file_path)
    print("Writing to output file complete")
