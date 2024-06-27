import sys
import os
from pkg.utils import get_refined_data


def main():
    assert len(sys.argv) == 4

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    threshold = float(sys.argv[3])

    get_refined_data(
        raw_reviews_path=input_file,
        output_file_path=output_file,
        rating_values=["good","bad"],
        model="en_core_web_lg",
        top_n_word=95,
        top_n_association=5,
        threshold=threshold
    )


if __name__ == "__main__":
    main()
