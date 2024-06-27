import sys
import os
from pkg.utils import get_refined_data


def main():
    assert len(sys.argv) == 5

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    model = sys.argv[3]
    threshold = float(sys.argv[4])

    get_refined_data(
        raw_reviews_path=input_file,
        output_file_path=output_file,
        rating_values=["good", "bad"],
        model=model,
        top_n_word=95,
        top_n_association=5,
        threshold=threshold,
    )


if __name__ == "__main__":
    main()
