#!/usr/bin/env python3
'''
copy files from raw file bucket to processed file bucket
'''
import sys
import argparse
import boto3
from dcicutils.ff_utils import get_metadata
from functions import script_utils as scu


def get_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[scu.create_ff_arg_parser(), scu.create_input_arg_parser()],
    )
    args = parser.parse_args()
    return args


def main():  # pragma: no cover
    # initial set up
    args = get_args(sys.argv[1:])
    auth = scu.authenticate(key=args.key, keyfile=args.keyfile, env=args.env)
    print("Working on {}".format(auth.get('server')))
    # bucket addresses
    ff_health = get_metadata('/health', auth)
    source_bucket = ff_health['file_upload_bucket']
    target_bucket = ff_health['processed_file_bucket']
    s3 = boto3.resource('s3')

    # get the uuids for the files
    uids = scu.get_item_ids_from_args(args.input, auth, args.search)
    files2copy = [get_metadata(uid, auth).get('upload_key') for uid in uids]

    for file_key in files2copy:
        copy_source = {'Bucket': source_bucket, 'Key': file_key}
        if args.dbupdate:
            try:
                s3.meta.client.copy(copy_source, target_bucket, file_key)
            except Exception:
                print('Can not find file on source', file_key)
                continue
        else:
            print("DRY RUN!")
        print(file_key + ' cp from ' + source_bucket + ' to ' + target_bucket)
        # print('{} file copied'.format(file_key))


if __name__ == '__main__':
    main()
