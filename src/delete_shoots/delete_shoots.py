import argparse
import boto3
import sys

def shoot_number_to_folder_path(shoot_number):
    """
    A shoot number consists of two letters followed by six digits
    >>> shoot_number = "CP000159"

    The files are arranged in folders according to the last two number of the shoot,
    and then by shoot number - In the folder name, the alphabetic prefix is separated from the
    rest of the number by an underscore

    >>> shoot_number_to_folder_path("CP000159")
    '59/CP_000159'
    """
    parent_folder = shoot_number[-2:]
    folder_name = "_".join([shoot_number[:2], shoot_number[2:]])
    return "/".join([parent_folder, folder_name])

def delete_s3_objects(session: boto3.session.Session, shoot_number: str, mode: str):
    s3 = session.resource('s3')
    bucket = s3.Bucket("wellcomecollection-editorial-photography")

    prefix = shoot_number_to_folder_path(shoot_number)

    objects_to_delete = bucket.objects.filter(Prefix=prefix)

    if mode == "dry-run":
        with open("planned_deletions.txt", "a") as file:
            file.writelines([f"{obj.key}\n" for obj in objects_to_delete])
    elif mode == "list-prefixes":
        with open("prefixes.txt", "a") as file:
            file.writelines(f"{prefix}\n")
    elif mode == "delete": 
      try: 
          s3.delete_objects(
            Bucket=bucket,
            Delete={
                'Objects': [{ "Key": obj.key } for obj in objects_to_delete]
            }
          )
      except Exception as err:
          with open("delete_failures.txt", "a") as file:
              file.write(err)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List the planned deletions or effect them.")
    parser.add_argument(
        "--mode",
        choices=["dry-run", "delete", "list-prefixes"],
        default="dry-run",
        help="Defaults to dry run: the planned deletions will be listed but not effected.",
    )
    args = parser.parse_args()

    for shoot in sys.stdin.readlines():
        delete_s3_objects(
            session=boto3.Session(profile_name="platform-read_only"),
            mode=args.mode,
            shoot_number=shoot.replace(" ", "").strip(),
        )        