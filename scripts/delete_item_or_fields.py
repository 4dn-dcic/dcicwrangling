#!/usr/bin/env python3
'''
Given a list of item IDs or search result will:
    1. given one of more values in the '--fields' options delete those fields from the item
    2. if no fields option then set the status of the item(s) to deleted
Useful for deleting multiple fields or changing item status to deleted
NOTE: can use patch_field_for_many_items script to delete a single field for many items
but this script is more direct/flexible in some ways
'''
import argparse
from dcicutils.ff_utils import get_metadata, delete_metadata, delete_field
from functions import script_utils as scu


def get_args(args):
    parser = argparse.ArgumentParser(
        parents=[scu.create_input_arg_parser(), scu.create_ff_arg_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--fields',
                        nargs='+',
                        help="With this option these fields will be removed from the items.")
    args = parser.parse_args(args)
    return args


def main():  # pragma: no cover
    args = get_args()
    auth = scu.authenticate(key=args.key, keyfile=args.keyfile, env=args.env)
    dry_run = True
    if args.dbupdate:
        dry_run = False

    print('#', auth.get('server'))
    id_list = scu.get_item_ids_from_args(args.input, auth, args.search)
    del_flds = None
    if args.fields:
        fields = args.fields
        del_flds = ','.join(fields)
    problems = []
    for iid in id_list:
        try:
            get_metadata(iid, auth, add_on='frame=object')
        except Exception:
            problems.append(iid)
            continue

        if del_flds:
            # we have field(s) that we want to delete from provided items
            print(f"Will delete {del_flds} from {iid}")
            if dry_run:
                print("DRY RUN")
            else:
                try:
                    res = delete_field(iid, del_flds, auth)
                    status = res.get('status')
                    if status.lower() == 'success':
                        print(status)
                    else:
                        print(res)
                        problems.append(iid)
                except Exception as e:
                    print(f"PROBLEM: {e}")
                    problems.append(iid)
        else:
            # we want to set the status of the items in id_list to deleted
            print(f"Will set status of {iid} to DELETED")
            if dry_run:
                print("DRY RUN")
            else:
                try:
                    res = delete_metadata(iid, auth)
                    status = res.get('status')
                    if status.lower() == 'success':
                        print(status)
                    else:
                        print(res)
                        problems.append(iid)
                except Exception as e:
                    print(f"PROBLEM: {e}")
                    problems.append(iid)

    if problems:
        print('THERE WAS A PROBLEM DELETING METADATA FOR THE FOLLOWING:')
        for p in problems:
            print(p)


if __name__ == '__main__':
    main()
