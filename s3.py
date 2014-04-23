import boto

config = {}
execfile("keys.conf", config)
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]

BUCKET_NAME = 'chattys3'

conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY)


import boto.s3
bucket = conn.get_bucket(BUCKET_NAME)




import sys
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

from boto.s3.key import Key
# testfile = "/home/josu/notas"
# print 'Uploading %s to Amazon S3 bucket %s' % (testfile, BUCKET_NAME)
# k = Key(bucket)
# k.key = 'my test file'
# k.set_contents_from_filename(testfile,
#     cb=percent_cb, num_cb=10)

key = bucket.get_key('my test file')
key.get_contents_to_filename('/tmp/test.txt')