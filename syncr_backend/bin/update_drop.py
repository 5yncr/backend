#!/usr/bin/env python
import argparse
import asyncio

from syncr_backend.metadata import drop_metadata
from syncr_backend.util import crypto_util
from syncr_backend.util import drop_util


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download the latest version for a drop",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        required=False,
        help="Directory of drop to updated",
    )
    parser.add_argument(
        "--drop_id",
        type=str,
        required=False,
        help="Drop ID to update",
    )
    return parser


def main() -> None:
    args = parser().parse_args()
    loop = asyncio.get_event_loop()

    if not (args.drop_id or args.save_dir):
        print("Either drop id or save dir must be specified")
        exit(1)

    if args.drop_id:
        drop_id = args.drop_id.encode('utf-8')
        drop_id = crypto_util.b64decode(drop_id)
    if not args.drop_id:
        drop_id = drop_util.get_drop_id_from_directory(args.save_dir)

    if drop_id is None:
        print("Drop ID not found")
        exit(1)

    md, update_avail = loop.run_until_complete(
        drop_util.check_for_update(drop_id),
    )
    if not update_avail or md is None:
        print("No update available, exiting")
        exit(0)

    drop_dir = loop.run_until_complete(
        drop_metadata.get_drop_location(drop_id),
    )

    done, _ = loop.run_until_complete(
        drop_util.sync_drop(drop_id, drop_dir, md.version),
    )

    if done:
        print("updated successfully")
        exit(0)
    else:
        print("did not update succussfully")
        exit(1)


if __name__ == '__main__':
    main()
