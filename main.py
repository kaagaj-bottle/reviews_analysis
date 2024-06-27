import sys
import os
from pkg.utils import get_refined_data


def main():
    assert len(sys.argv) == 3

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    get_refined_data(
        raw_reviews_path=input_file,
        output_file_path=output_file,
        rating_values=["good","bad"],
        model="en_core_web_md",
        top_n_word=95,
        top_n_association=5,
        threshold=0.8
    )


if __name__ == "__main__":
    main()
