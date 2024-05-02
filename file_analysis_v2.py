import os
import sys
import subprocess
import argparse
from datetime import datetime
import csv

def print_usage():
    print("""
  Usage: file_analysis.py <Analysis Type> <Path To Analyze>

     Flag    Analysis Type
     -s      Breakdown by File Size
     -c      Breakdown by File Creation Days
     -m      Breakdown by File Modification Days
     -a      Breakdown by File Access Days
     -ac     Breakdown by File Access Days, Output in CSV
     -u      Breakdown by UID
     -g      Breakdown by GID

  Please Note:
    You will need to modify the work_dir variable to match your system.
    You will need to modify the node_class variable to match your system. If
    you want to use the default, you can set the value to ''.
""")

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

def setup_work_area(work_dir):
    os.makedirs(work_dir, exist_ok=True)
    policy_file = os.path.join(work_dir, "policy.in")
    log_file = os.path.join(work_dir, "policy.out")
    return policy_file, log_file

def apply_policy(analysis_path, work_dir, node_class, policy_file, log_file):
    command = f"/usr/lpp/mmfs/bin/mmapplypolicy {analysis_path} -f {work_dir} -g {work_dir} {node_class} -P {policy_file} -I defer"
    with open(log_file, "w") as log:
        subprocess.run(command, shell=True, stdout=log, stderr=subprocess.STDOUT)

def file_info(directory):
    files_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            stats = os.stat(filepath)
            file_data = {
                'name': file,
                'size': stats.st_size,
                'creation_time': datetime.fromtimestamp(stats.st_ctime),
                'modification_time': datetime.fromtimestamp(stats.st_mtime),
                'access_time': datetime.fromtimestamp(stats.st_atime),
                'uid': stats.st_uid,
                'gid': stats.st_gid
            }
            files_info.append(file_data)
    return files_info

def display_files_info(files_info, analysis_type):
    if analysis_type == 'accesscsv':
        with open('access_times.csv', 'w', newline='') as csvfile:
            fieldnames = ['name', 'access_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for file_data in files_info:
                writer.writerow({'name': file_data['name'], 'access_time': file_data['access_time'].strftime('%Y-%m-%d %H:%M:%S')})
        print("Access times report saved to access_times.csv")
    else:
        for file_data in files_info:
            if analysis_type in ['size', 'creation', 'modification', 'access', 'uid', 'gid']:
                print(f"{file_data['name']}: {file_data[analysis_type]}")

def main():
    args = parse_args()
    work_dir = "/tmp/policy.{}".format(os.getpid())
    policy_file, log_file = setup_work_area(work_dir)

    # Dummy apply_policy to demonstrate the concept
    apply_policy(args.directory, work_dir, '', policy_file, log_file)
    
    files_info = file_info(args.directory)
    if args.size:
        display_files_info(files_info, 'size')
    elif args.creation:
        display_files_info(files_info, 'creation')
    elif args.modification
