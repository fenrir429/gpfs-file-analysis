import os
import argparse
from datetime import datetime
import csv
import pwd
import grp

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze files in a directory based on various criteria.")
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('-s', '--size', action='store_true', help='Breakdown by File Size')
    parser.add_argument('-c', '--creation', action='store_true', help='Breakdown by File Creation Days')
    parser.add_argument('-m', '--modification', action='store_true', help='Breakdown by File Modification Days')
    parser.add_argument('-a', '--access', action='store_true', help='Breakdown by File Access Days')
    parser.add_argument('-ac', '--accesscsv', action='store_true', help='Breakdown by File Access Days, Output in CSV')
    parser.add_argument('-u', '--uid', action='store_true', help='Breakdown by UID (Usernames)')
    parser.add_argument('-g', '--gid', action='store_true', help='Breakdown by GID (Group Names)')
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
                'size': stats.st_size,
                'creation_time': (now - datetime.fromtimestamp(stats.st_ctime)).days,
                'modification_time': (now - datetime.fromtimestamp(stats.st_mtime)).days,
                'access_time': (now - datetime.fromtimestamp(stats.st_atime)).days,
                'username': pwd.getpwuid(stats.st_uid).pw_name,
                'groupname': grp.getgrgid(stats.st_gid).gr_name
            }
            files_info.append(file_data)
    return files_info

def categorize_files(files_info, key):
    buckets = {}
    if key == 'size':
        size_ranges = [
            (1024, '<1KB'), (64*1024, '1KB-64KB'), (128*1024, '64KB-128KB'), 
            (256*1024, '128KB-256KB'), (512*1024, '256KB-512KB'), (1024**2, '512KB-1MB'),
            (2*1024**2, '1MB-2MB'), (4*1024**2, '2MB-4MB'), (8*1024**2, '4MB-8MB'),
            (16*1024**2, '8MB-16MB'), (100*1024**2, '16MB-100MB'), (256*1024**2, '100MB-256MB'),
            (512*1024**2, '256MB-512MB'), (1024**3, '512MB-1GB'), (5*1024**3, '1GB-5GB'),
            (float('inf'), '>5GB'),
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
    else:
        for file_data in files_info:
            days = file_data[key]
            if days == 0:
                bucket_key = 'Today'
            elif days <= 7:
                bucket_key = 'This Week'
            elif days <= 30:
                bucket_key = 'This Month'
            else:
                bucket_key = 'Older'
            if bucket_key not in buckets:
                buckets[bucket_key] = {'count': 0, 'bytes': 0}
            buckets[bucket_key]['count'] += 1
            buckets[bucket_key]['bytes'] += size
    return buckets

def display_buckets(buckets):
    print(f"{'Category':<20} {'# of Files':<15} {'# of Bytes':<15}")
    for key, data in sorted(buckets.items(), key=lambda item: item[1]['count'], reverse=True):
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
    key = 'size' if args.size else \
          'creation_time' if args.creation else \
          'modification_time' if args.modification else \
          'access_time' if args.access else \
          'username' if args.uid else \
          'groupname' if args.gid else None

    if not key:
        print("No valid analysis type provided. Use -h for help.")
        return

    buckets = categorize_files(files_info, key)
    if args.outputcsv or args.accesscsv:
        filename = f"{key}_data.csv"
        output_to_csv(buckets, filename)
    else:
        display_buckets(buckets)

if __name__ == "__main__":
    main()
