import boto3
from botocore.exceptions import NoCredentialsError
import os
import requests
from dotenv import load_dotenv
load_dotenv()

def upload_to_aws(local_file, s3_file_name):
    bucket = "synclabsbucket"
    s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))

    try:
        s3.upload_file(local_file, bucket, s3_file_name, ExtraArgs={'ACL': 'public-read'})
        print("Upload Successful")
        return f"https://{bucket}.s3.amazonaws.com/{s3_file_name}"
    
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None


def upload_link_file_to_aws(file_link, s3_file_name):
    # Download the video file from the link
    response = requests.get(file_link)
    if response.status_code == 200:
        # Save the video file locally
        local_file = "original_vid.mp4"
        with open(local_file, 'wb') as f:
            f.write(response.content)
        
        # Upload the video file to S3
        return upload_to_aws(local_file, s3_file_name)
    else:
        print("Failed to download the video file")
        return None