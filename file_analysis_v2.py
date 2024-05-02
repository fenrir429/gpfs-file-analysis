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
        if key == 'size':
            if file_data[key] < 1024:
                bucket = '<1KB'
            elif file_data[key] < 1024**2:
                bucket = '<1MB'
            elif file_data[key] < 1024**3:
                bucket = '<1GB'
            else:
                bucket = '>1GB'
        else:
            days = file_data[key]
            if days == 0:
                bucket = 'Today'
            elif days == 1:
                bucket = 'Yesterday'
            elif days <= 7:
                bucket = 'Last 7 Days'
            elif days <= 30:
                bucket = 'Last 30 Days'
            else:
                bucket = 'Older than 30 Days'
        if bucket not in buckets:
            buckets[bucket] = {'count': 0, 'bytes': 0}
        buckets[bucket]['count'] += 1
        buckets[bucket]['bytes'] += file_data['size']
    return buckets

def display_buckets(buckets):
    print(f"{'Category':<20} {'# of Files':<15} {'# of Bytes':<15}")
    for key, data in sorted(buckets.items()):
        print(f"{key:<20} {data['count']:>15} {data['bytes']:>15}")

def output_to_csv(buckets, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Category', 'Count', 'Bytes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, data in buckets.items():
            writer.writerow({'Category': key, 'Count': data['count'], 'Bytes': data['bytes']})
    print(f"Access times report saved to {filename}")

def main():
    args = parse_args()
    files_info = file_info(args.directory)

    if args.size:
        key = 'size'
    elif args.creation:
        key = 'creation_time'
    elif args.modification:
        key = 'modification_time'
    elif args.access or args.accesscsv:
        key = 'access_time'
    elif args.uid:
        key = 'uid'
    elif args.gid:
        key = 'gid'
    else:
        print("No valid analysis type provided. Use -h for help.")
        return

    buckets = categorize_files(files_info, key)
    if args.accesscsv:
        output_to_csv(buckets, "access_times.csv")
    else:
        display_buckets(buckets)

if __name__ == "__main__":
    main()
