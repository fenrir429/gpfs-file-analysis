import os
import argparse
from datetime import datetime, timedelta
import csv
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze files in a directory based on various criteria.")
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('-s', '--size', action='store_true', help='Breakdown by File Size')
    parser.add_argument('-c', '--creation', action='store_true', help='Breakdown by File Creation Days')
    parser.add_argument('-m', '--modification', action='store_true', help='Breakdown by File Modification Days')
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
                'size': stats.st_size,
                'creation_time': (now - datetime.fromtimestamp(stats.st_ctime)).days,
                'modification_time': (now - datetime.fromtimestamp(stats.st_mtime)).days,
            }
            files_info.append(file_data)
    return files_info

def categorize_files(files_info, key):
    buckets = {}
    if key in ['creation_time', 'modification_time']:
        for file_data in files_info:
            days = file_data[key]
            bucket_key = f"{days} days old"
            if bucket_key not in buckets:
                buckets[bucket_key] = {'count': 0, 'bytes': 0}
            buckets[bucket_key]['count'] += 1
            buckets[bucket_key]['bytes'] += file_data['size']
    elif key == 'size':
        size_ranges = [
            (4*1024, '<4K'), (64*1024, '4K - 64K'), (128*1024, '64K - 128K'), 
            (256*1024, '128K - 256K'), (512*1024, '256K - 512K'), (1024**2, '512K - 1M'),
            (2*1024**2, '1M - 2M'), (4*1024**2, '2M - 4M'), (8*1024**2, '4M - 8M'),
            (16*1024**2, '8M - 16M'), (100*1024**2, '16M - 100M'), (256*1024**2, '100M - 256M'),
            (512*1024**2, '256M - 512M'), (1024**3, '512M - 1G'), (5*1024**3, '1G - 5G'),
            (float('inf'), '>5G'),
        ]
        for file_data in files_info:
            size = file_data['size']
            for limit, label in size_ranges:
                if size <= limit:
                    if label not in buckets:
                        buckets[label] = {'count': 0, 'bytes': 0}
                    buckets[label]['count'] += 1
                    buckets[label]['bytes'] += size
                    break
    return buckets

def display_buckets(buckets):
    print(f"{'Category':<20} {'# of Files':<15} {'# of Bytes':<15}")
    for key, data in sorted(buckets.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"{key:<20} {data['count']:>15} {data['bytes']:>15}")

def main():
    args = parse_args()
    files_info = file_info(args.directory)

    if args.size:
        key = 'size'
    elif args.creation:
        key = 'creation_time'
    elif args.modification:
        key = 'modification_time'
    else:
        print("No valid analysis type provided. Use -h for help.")
        sys.exit(1)

    buckets = categorize_files(files_info, key)
    display_buckets(buckets)

if __name__ == "__main__":
    main()
