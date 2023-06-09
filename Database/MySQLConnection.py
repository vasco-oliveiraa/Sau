from contextlib import contextmanager
import mysql.connector
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
import json

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the relative path to your .env file
dotenv_path = os.path.join(current_dir, "..", ".env")

# Load environment variables from the .env file
load_dotenv(dotenv_path)

def get_secret():
    secret_name = "rds!db-9cdf7c4e-7852-4006-bc78-de06f0584885"
    region_name = os.getenv("AWS_REGION")

    # Add your AWS credentials here
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Create a Secrets Manager client
    session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret

@contextmanager
def my_sql_connection():
    secret = get_secret()
    secret_json = json.loads(secret)

    mydb = mysql.connector.connect(
        host= "sau.c6l5guiieo6w.eu-west-3.rds.amazonaws.com", #'localhost',
        user= secret_json['username'], #'root', 
        password= secret_json['password'] #'bigdata'
    )
    c = mydb.cursor()
    try:
        yield c
        mydb.commit()
    except Exception as e:
        mydb.rollback()
        raise e
    finally:
        c.close()
        mydb.close()