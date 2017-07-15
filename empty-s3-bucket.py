import boto3
client = boto3.client('s3')
bucket = "savordel-big"
# print("Collecting data from" + bucket)
paginator = client.get_paginator('list_object_versions')
result = paginator.paginate(Bucket=bucket)
objects = []
# paginator iterator
for page in result:
    # check fi there is files, if there isn't, go to delete bucket
    try:
        for k in page['Versions']:
            objects.append({
                'Key': k['Key'],
                'VersionId': k['VersionId']
            })
        try:
            for k in page['DeleteMarkers']:
                version = k['VersionId']
                key = k['Key']
                objects.append({
                    'Key': key,
                    'VersionId': version
                })
        except:
            pass

        client.delete_objects(Bucket=bucket, Delete={'Objects': objects})
        objects = []
    except:
        pass
        # print("bucket already empty")

    """
    Try to delete, if fails, remove the bucket policy and try again
    That's for delete operation inconsistency. S3 is distributed system, so
    it can take some time to delete the objects in all servers.  This is why there is the sleep(10)
    After delete the objects the object must be removed from all servers, which happens after 200 - OK
    """
try:
    client.delete_bucket(Bucket=bucket)
except:
    client.delete_bucket_policy(Bucket=bucket)
    sleep(10)
    client.delete_bucket(Bucket=bucket)
    raise Exception("bucket not widely empty, try again later - The bucket is empty, though")


