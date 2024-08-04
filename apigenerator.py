import json
import boto3
from botocore.exceptions import ClientError

# Initialize clients
api_gateway = boto3.client('apigateway')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

sns_topic_arn = 'arn:aws:sns:us-east-1:197807873055:VerityVaultKeys'
usage_plan_id = 'aj5e5t'
dynamo_table_name = 'verity_vault_keys'

def lambda_handler(event, context):
    try:
        # Parse email from the request body
        user_email = json.loads(event['body'])['email']

        # Check if the email already has an API key
        table = dynamodb.Table(dynamo_table_name)
        response = table.get_item(
            Key={'email': user_email}
        )

        if 'Item' in response:
            # Email already has an API key, send existing key
            api_key_value = response['Item']['apiKey']
            send_email(user_email, api_key_value)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Email already subscribed. Existing API key sent.'})
            }
        else:
            # Create new API key
            api_key_response = api_gateway.create_api_key(
                name=f"APIKey-{user_email}",
                enabled=True
            )
            api_key = api_key_response['id']
            api_key_value = api_key_response['value']

            # Associate API key with usage plan
            api_gateway.create_usage_plan_key(
                keyId=api_key,
                keyType='API_KEY',
                usagePlanId=usage_plan_id
            )

            # Store user and API key in DynamoDB
            table.put_item(
                Item={
                    'email': user_email,
                    'apiKey': api_key_value
                }
            )

            # Check if email is already subscribed to SNS topic
            if not is_subscribed_to_sns(user_email):
                # Subscribe email to SNS topic
                sns.subscribe(
                    TopicArn=sns_topic_arn,
                    Protocol='email',
                    Endpoint=user_email
                )

            # Send email with API key
            send_email(user_email, api_key_value)

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'API key generated, email subscribed to SNS topic, and email sent'})
            }

    except ClientError as error:
        print(f"Error generating API key: {error}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error generating API key'})
        }

def is_subscribed_to_sns(email):
    try:
        response = sns.list_subscriptions_by_topic(
            TopicArn=sns_topic_arn
        )
        subscriptions = response['Subscriptions']
        for sub in subscriptions:
            if sub['Protocol'] == 'email' and sub['Endpoint'] == email:
                return True
        return False
    except ClientError as e:
        print(f"Error checking SNS subscription: {e}")
        return False

def send_email(to, api_key):
    try:
        subject = "Your API Key"
        message = f"Your API key is: {api_key}"

        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=subject,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'VerityVault'  # Ensure this is 1-11 alphanumeric or hyphen characters
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        print(f"Email sent to {to} with API key: {api_key}")

    except ClientError as e:
        print(f"Error sending email: {e}")
        raise e
