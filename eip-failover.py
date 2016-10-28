import boto3
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s - %(funcName)s - %(message)s',
    datefmt='%Y-%b-%d %I:%M:%S %p'
)
logger = logging.getLogger(__name__)

region = 'us-east-1'
instances = ['i-xxxxxxx', 'i-xxxxxxx']
eip = '5x.xxx.xxx.xxx'


def failover(unhealthy_ec2):
    '''
    Remove the EIP from unhealthy instance then assign it
    to another server after doing health checks
    '''
    try:
        instances.remove(unhealthy_ec2)
        healthy_ec2 = instances[0]
        ec2 = boto3.client('ec2', region_name=region)
        describe_response = ec2.describe_addresses(
            PublicIps=[
                eip
            ]
        )
        assoc_id = describe_response['Addresses'][0]['AssociationId']
        disassociate_response = ec2.disassociate_address(
            AssociationId=assoc_id
        )
        disassociate_status_code = disassociate_response['ResponseMetadata'][
            'HTTPStatusCode'
        ]
        alloc_id = describe_response['Addresses'][0]['AllocationId']

        logger.info('Disassociating {0} from {1}...'.format(
            eip, unhealthy_ec2)
        )

        if disassociate_status_code == 200:
            associate_response = ec2.associate_address(
                InstanceId=healthy_ec2,
                AllocationId=alloc_id
            )

            logger.info('Associating {0} to {1}...'.format(eip, healthy_ec2))
            return associate_response
        else:
            return disassociate_response
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as e:
        logger.error(e, exc_info=True)


def check_eip(unhealthy_ec2):
    '''
    Check IP if it matches the Elastic IP before doing a failover
    '''
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        public_ip = ec2.Instance(unhealthy_ec2).public_ip_address

        if public_ip == eip:
            logger.info('PublicIP: {0} == EIP: {1}'.format(public_ip, eip))
            return failover(unhealthy_ec2)
        else:
            logger.info('Nothing to do here.')
            sys.exit(0)
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as e:
        logger.error(e, exc_info=True)


def main(event, context):
    alarm = json.loads(event['Records'][0]['Sns']['Message'])['AlarmName']
    state = json.loads(event['Records'][0]['Sns']['Message'])['NewStateValue']
    unhealthy_ec2 = json.loads(
        event['Records'][0]['Sns']['Message']
    )['Trigger']['Dimensions'][0]['value']

    logger.info('Alarm:', alarm)
    logger.info('State:', state)
    logger.info(check_eip(unhealthy_ec2))
