import click

from . import bucket


@click.group()
def gcloud() -> None:
    """Google Cloud related commands"""


gcloud.add_command(bucket.bucket_group)
