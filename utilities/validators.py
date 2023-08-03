import csv
import os


def is_csv(csv_file_path) -> bool:
    if csv_file_path is None:
        print("CSV file not provided.")
        return False

    if not os.path.isfile(csv_file_path):
        print(f"CSV does not exist at path {csv_file_path}.")
        return False

    try:
        with open(csv_file_path) as f:
            csv.Sniffer().sniff(f.read(4096))
    except csv.Error:
        return False

    return True


def is_none_or_empty_string(string: str) -> bool:
    return string is None or len(string.strip()) == 0
