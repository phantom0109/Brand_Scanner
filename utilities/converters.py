import csv
import hashlib


def csv_to_dict_list(csv_file_path):
    arr = []

    with open(csv_file_path, encoding="utf-8") as csvf:
        csv_reader = csv.DictReader(csvf)
        for row in csv_reader:
            arr.append(row)

    return arr


def str_to_md5(string) -> str:
    return hashlib.md5(string.encode()).hexdigest()
