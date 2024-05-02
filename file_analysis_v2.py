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

def categorize_files(files_info, key, bucket_func=None):
    buckets = {}
    for file_data in files_info:
        bucket_key = bucket_func(file_data[key]) if bucket_func else file_data[key]
        if bucket_key not in buckets:
            buckets[bucket_key] = {'count': 0, 'bytes': 0}
        buckets[bucket_key]['count'] += 1
        buckets[bucket_key]['bytes'] += file_data['size']
    return buckets

def display_buckets(buckets):
    for key, data in sorted(buckets.items()):
        print(f"{key:<20} {data['count']:>10} {data['bytes']:>20}")

def main():
    args = parse_args()
    files_info = file_info(args.directory)

    if args.size:
        buckets = categorize_files(files_info, 'size', lambda x: f"<{x // 1024}K" if x < 1024**2 else f"<{x // (1024**2)}M")
    elif args.creation or args.modification or args.access:
        date_key = 'creation_time' if args.creation else 'modification_time' if args.modification else 'access_time'
        buckets = categorize_files(files_info, date_key)
    elif args.uid or args.gid:
        user_key = 'uid' if args.uid else 'gid'
        buckets = categorize_files(files_info, user_key)
    elif args.accesscsv:
        buckets = categorize_files(files_info, 'access_time')
        with open('access_times.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'count', 'bytes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for key, data in sorted(buckets.items()):
                writer.writerow({'date': key, 'count': data['count'], 'bytes': data['bytes']})
        print("Access times report saved to access_times.csv")
        return

    display_buckets(buckets)

if __name__ == "__main__":
    main()
