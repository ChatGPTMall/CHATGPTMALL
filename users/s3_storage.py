from storages.backends.s3boto3 import S3Boto3Storage


class ItemVideosS3Storage(S3Boto3Storage):
    bucket_name = 'madeinthai'
    location = 'item_videos'