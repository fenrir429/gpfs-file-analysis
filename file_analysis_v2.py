import os
import argparse
from datetime import datetime
import csv
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze files in a directory based on various criteria.")
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('-s', '--size', action='store_true', help='Breakdown by File Size')
    parser.add_argument('-c', '--creation', action='store_true', help='Breakdown by File Creation Days')
    parser.add_argument('-m', '--modification', action='store_true', help='Breakdown by File Modification Days')
    parser.add_argument('-a', '--access', action='store_true', help='Breakdown by File Access Days')
    parser.add_argument('-ac', '--accesscsv', action='store_true', help='Breakdown by File Access Days, Output in CSV')
    parser.add_argument('-u', '--uid', action='store_true', help='Breakdown by UID')
    parser.add_argument('-g', '--gid', action='store_true', help='Breakdown by GID')
    args = parser.parse_args()
    return args

def file_info(directory):
    files_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            stats = os.stat(filepath)
            file_data = {
                'name': file,
                'size': stats.st_size,
                'creation_time': datetime.fromtimestamp(stats.st_ctime).date(),
                'modification_time': datetime.fromtimestamp(stats.st_mtime).date(),
                'access_time': datetime.fromtimestamp(stats.st_atime).date(),
                'uid': stats.st_uid,
                'gid': stats.st_gid
            }
            files_info.append(file_data)
    return files_info

def categorize_files(files_info, key):
    buckets = {}
    for file_data in files_info:
        identifier = file_data[key]
        if identifier not in buckets:
            buckets[identifier] = {'count': 0, 'bytes': 0}
        buckets[identifier]['count'] += 1
        buckets[identifier]['bytes'] += file_data['size']
    return buckets

def display_buckets(buckets):
    print(f"{'Category':<20} {'# of Files':<15} {'# of Bytes':<15}")
    for key, data in sorted(buckets.items()):
        print(f"{key:<20} {data['count']:>15} {data['bytes']:>15}")

def output_to_csv(buckets, filename="output.csv"):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Category', 'Count', 'Bytes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, data in sorted(buckets.items()):
            writer.writerow({'Category': key, 'Count': data['count'], 'Bytes': data['bytes']})

def main():
    args = parse_args()
    files_info = file_info(args.directory)

    if args.size:
        key = 'size'
    elif args.creation:
        key = 'creation_time'
    elif args.modification:
        key = 'modification_time'
    elif args.access:
        key = 'access_time'
    elif args.uid:
        key = 'uid'
    elif args.gid:
        key = 'gid'
    else:
        print("No valid analysis type provided. Use -h for help.")
        sys.exit(1)

    buckets = categorize_files(files_info, key)

    if args.accesscsv:
        output_to_csv(buckets, "access_times.csv")
        print("Access times report saved to access_times.csv")
    else:
        display_buckets(buckets)

if __name__ == "__main__":
    main()
