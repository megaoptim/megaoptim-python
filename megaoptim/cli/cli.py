import logging
import argparse
import os
import sys
import csv
import errno
import time
import datetime
import requests
import traceback

from megaoptim.client.client import Client

log = logging.getLogger(__name__)


def log_output(args, text, level="standard"):
    current_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    if 'quiet' in args and args.quiet == 1:
        return
    if level == 'verbose':
        if 'verbose' in args and args.verbose == 1:
            print(current_time + " - " + text)
    else:
        print(current_time + " - " + text)


def create_args():
    parser = argparse.ArgumentParser(prog='megaoptim',description='Commandline interface for MegaOptim Image Optimizer')

    parser.add_argument(
        '--api-key',
        help='The api key obtained from MegaOptim.com. This is required for the script to run!',
    )

    parser.add_argument(
        '--dir',
        help='Full or relative path to directory that you want to be optimized.',
    )

    parser.add_argument(
        '--outdir',
        help='Full or relative path to directory that you want to use to store the optimized path. Warning: If you don\'t '
             'specify this the files in the original directory will be overwritten! '
    )

    parser.add_argument(
        '--compression',
        default='intelligent',
        help='Lossy or lossless compression. The lossy method will automatically choose best quality level for the human '
             'vision. It can save you up to 90%% of the initial file size and still give outstanding results.',
        choices=['intelligent', 'ultra', 'lossless']
    )

    parser.add_argument(
        '--keep-exif',
        default='0',
        help='1 to keep the exif data, 0 to strip the exif data.',
        choices=['1', '0']
    )

    parser.add_argument(
        '--cmyktorgb',
        default='1',
        help='1 to force all CMYK to sRGB, 0 to preserve their CMYK profile.',
        choices=['1', '0']
    )

    parser.add_argument(
        '--max-width',
        default='0',
        help='Image will be resized to maximum width value specified. Ratio will be preserved!',
    )

    parser.add_argument(
        '--max-height',
        default='0',
        help='Image will be resized to maximum height value specified. Ratio will be preserved!',

    )

    parser.add_argument(
        '--exclude',
        default='0',
        help='Comma separated full paths of folders. Eg. "/path/to/folder1,/path/to/folder2"',

    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Outputs useful information about the optimization.'
    )
    group.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Suppresses all the output.'
    )

    group.add_argument(
        '-r',
        '--recursive',
        default='0',
        choices=['1', '0'],
        help='If selected 1 it will optimize the images recursively.'
    )

    return parser.parse_args()


def prepare_api_params(args):
    params = {}
    if 'compression' in args:
        params['compression'] = args.compression
    if 'cmyktorgb' in args:
        params['cmyktorgb'] = args.cmyktorgb
    if 'keep_exif' in args:
        params['keep_exif'] = args.keep_exif
    if 'max_width' in args:
        params['max_width'] = args.max_width
    if 'max_width' in args:
        params['max_width'] = args.max_width
    return params


def download_url(url, save_path):
    if not os.path.isdir(save_path) and os.path.exists(save_path):
        os.remove(save_path)
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return os.path.exists(save_path)


def get_data_dir_path(path):
    return path + os.sep + '.megaoptim'


def get_optimized_paths(args, data_storage_path):
    optimized = []
    if not os.path.exists(data_storage_path) or not os.path.isfile(data_storage_path):
        return optimized
    with open(data_storage_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for i in csv_reader:
            optimized.append(i['old_path'])
    return optimized


def find_files_recursively(treeroot):
    file_iterator = (os.path.join(root, f)
                for root, _, files in os.walk(treeroot)
                for f in files)
    files = (f for f in file_iterator if (os.path.splitext(f)[1] in ['.jpg', '.jpeg', '.png', '.gif']))
    return list(files)


def find_files(treeroot):
    return [os.path.join(treeroot, f) for f in os.listdir(treeroot) if (os.path.splitext(f)[1] in ['.jpg', '.jpeg', '.png', '.gif'])]


def scan_directory(args, directory, recursive):
    if recursive:
        found_files = find_files_recursively(directory)
    else:
        found_files = find_files(directory)

    # Create unique directories list and collect all the optimized paths.
    # If recursive=true it will go recursively.
    directories = []
    optimized = []
    for file in found_files:
        directories.append(os.path.dirname(file))
    directories = list(set(directories))

    for subDirectory in directories:
        _optimized_paths = get_optimized_paths(args, get_data_dir_path(subDirectory))
        if len(_optimized_paths) > 0:
            optimized.extend(_optimized_paths)

    if len(optimized) > 0:
        filtered = [x for x in found_files if x not in optimized]
        found_files = filtered
        del filtered

    return found_files


def save_result(args, result):
    original_dir = os.path.dirname(result['old_path'])
    data_storage_path = get_data_dir_path(original_dir)
    keys = result.keys()
    first_time = False
    if not os.path.exists(data_storage_path):
        first_time = True
    with open(data_storage_path, 'a+') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        # if this is first time creation of the file then append header
        if first_time:
            dict_writer.writeheader()
        dict_writer.writerow(result)


def save_file(args, url, save_path):
    status = download_url(url, save_path)
    if status is True:
        return save_path
    return status


def dump_object(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))


def optimize_dir(args, client, currentdir, outdir, params, recursive):
    files = list(scan_directory(args, currentdir, recursive))

    if len(files) == 0:
        print('No unoptimized files found.')
        return

    total_count = len(files)
    optimized_count = 0
    total_saved = 0
    total_size = 0

    log_output(args, "Found total " + str(total_count) + " images", level="verbose")
    for item in files:
        file_name = os.path.basename(item)
        if outdir is None or outdir == 0:
            save_path = item
        else:
            if not os.path.isdir(outdir):
                try:
                    os.mkdir(outdir)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
                    pass
            save_path = outdir + os.sep + file_name
        log_output(args, "Checking if the target path " + save_path + " is writable...", level="verbose")
        if outdir is not None and not os.access(outdir, os.W_OK):
            raise Exception("The save directory " + outdir + " is not writable :(")
        else:
            log_output(args, "Processing file " + os.path.basename(item))
            r = client.optimize(item, params)
            if r.get('status') == 'ok' and r.get('code') == 200:
                # Loop through results array from the response to get optimization info for every image in the request
                for ritem in r.get('result'):
                    if ritem['url'] is None:
                        log_output(args,"Failed to save file " + os.path.basename(item) + ": Missing optimization url.")
                        continue
                    ritem['old_path'] = item
                    ritem['optimized_path'] = save_file(args, url=ritem['url'], save_path=save_path)
                    if not ritem['optimized_path']:
                        log_output(args, "Failed to optimize file " + os.path.basename(item))
                    else:
                        log_output(args, "File " + os.path.basename(item) + " successfully optimized.")
                        ritem['date'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                        optimized_count = optimized_count + 1
                        if ritem['saved_bytes'] <= 0:
                            total_saved = 0
                        else:
                            total_saved += (ritem['saved_bytes'] / 1024) / 1024
                        total_size += ritem['original_size']
                        save_result(args, ritem)

    overall_total_size = (total_size / 1024) / 1024
    overall_total_size = round(overall_total_size, 2)
    total_saved = round(total_saved, 2)

    log_output(args, "Directory " + currentdir + " successfully optimized!\n Total files count: " + str(
        optimized_count) + " (" + str(overall_total_size) + " MB). Total space saved: " + str(
        total_saved) + " MB")


def do():
    args = create_args()
    params = prepare_api_params(args)

    api_key = None

    # The api key is required. Bail if empty!
    if 'api_key' in args:
        api_key = args.api_key
    if api_key is None:
        print('Please enter valid API key. Sign up at megaoptim.com for one if you dont have.')
        exit()

    # If --dir is not specified it will fallback to the current working directory.
    if 'dir' in args and args.dir is not None:
        working_dir = os.path.realpath(args.dir)
    else:
        working_dir = os.getcwd()

    # If --outdir is not specified it will overwrite the files of the current direcotry. Use this with caution!
    if 'outdir' in args and args.outdir is not None:
        if(os.path.exists(args.outdir)):
            outdir = os.path.realpath(args.outdir)
        else:
            outdir = None
            print('The specified outdir does not exist.')
            exit()
    else:
        outdir = None

    if 'recursive' in args and args.recursive == '0':
        recursive = False
    else:
        recursive = True

    try:
        client = Client(api_key)
        optimize_dir(args, client, working_dir, outdir, params, recursive)
    except Exception as e:
        print(traceback.format_exc())

