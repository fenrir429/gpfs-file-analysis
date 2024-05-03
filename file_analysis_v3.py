import os
import argparse
from datetime import datetime
import csv

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
    parser.add_argument('-csv', '--outputcsv', action='store_true', help='Output results to CSV file')
    args = parser.parse_args()
    return args

def file_info(directory):
    now = datetime.now()
    files_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            stats = os.stat(filepath)
            file_data = {
                'name': file,
                'path': filepath,
                'size': stats.st_size,
                'creation_time': (now - datetime.fromtimestamp(stats.st_ctime)).days,
                'modification_time': (now - datetime.fromtimestamp(stats.st_mtime)).days,
                'access_time': (now - datetime.fromtimestamp(stats.st_atime)).days,
                'uid': stats.st_uid,
                'gid': stats.st_gid
            }
            files_info.append(file_data)
    return files_info

def categorize_files(files_info, key):
    buckets = {}
    for file_data in files_info:
        identifier = str(file_data[key])
        if key in ['creation_time', 'modification_time', 'access_time']:
            days = int(identifier)
            bucket_key = f"{days} days old" if days > 0 else 'Today'
        else:
            bucket_key = identifier
        if bucket_key not in buckets:
            buckets[bucket_key] = {'count': 0, 'bytes': 0}
        buckets[bucket_key]['count'] += 1
        buckets[bucket_key]['bytes'] += file_data['size']
    return buckets

def display_buckets(buckets):
    print(f"{'Category':<20} {'# of Files':<15} {'# of Bytes':<15}")
    for key, data in sorted(buckets.items(), key=lambda item: item[0]):
        print(f"{key:<20} {data['count']:>15} {data['bytes']:>15}")

def output_to_csv(buckets, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Category', 'Count', 'Bytes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, data in buckets.items():
            writer.writerow({'Category': key, 'Count': data['count'], 'Bytes': data['bytes']})
    print(f"Results saved to {filename}")

def main():
    args = parse_args()
    files_info = file_info(args.directory)
    key = 'size' if args.size else 'creation_time' if args.creation else 'modification_time' if args.modification else 'access_time' if args.access else 'uid' if args.uid else 'gid' if args.gid else None
    if not key:
        print("No valid analysis type provided. Use -h for help.")
        return

    buckets = categorize_files(files_info, key)
    if args.outputcsv:
        filename = f"{key}_data.csv"
        output_to_csv(buckets, filename)
    else:
        display_buckets(buckets)

if __name__ == "__main__":
    main()
