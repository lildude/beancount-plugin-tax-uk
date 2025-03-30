from pathlib import Path
from cgtcalc_parser import parse_file


def process_cgtcalc_files():
    # Define input and output directories
    input_dir = Path("tests/data/cgtcalc_inputs")
    output_dir = Path("tests/data/cgtcalc_inputs_beancount")

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Process each file in the input directory
    for input_file in input_dir.glob("*"):
        if input_file.is_file():
            # Generate output filename by replacing/adding .beancount extension
            output_file = output_dir / f"{input_file.stem}.beancount"

            try:
                # Parse the input file and write results to output file
                beancount_content = parse_file(str(input_file))
                with open(output_file, "w") as f:
                    f.write(beancount_content)
                print(f"Processed {input_file} -> {output_file}")
            except Exception as e:
                print(f"Error processing {input_file}: {str(e)}")


if __name__ == "__main__":
    process_cgtcalc_files()
