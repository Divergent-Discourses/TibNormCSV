import argparse
from configparser import ConfigParser
from module import load_tables, process_csv

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Normalise text in a CSV file.")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("output_csv", help="Path to save the output CSV file")
    args = parser.parse_args()

    config = ConfigParser()

    with open('src/config.ini', encoding="utf-8") as f:
        config.read_file(f)

    # load replacement tables
    tables = load_tables(config)

    # Process the CSV
    process_csv(args.input_csv, args.output_csv, tables)


if __name__ == '__main__':
    main()
