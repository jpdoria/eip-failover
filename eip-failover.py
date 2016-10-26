import sys
import boto3

region = 'us-east-1'
instances = ['i-xxxxxxxx', 'i-xxxxxxxx']
eip = '5x.xx.xxx.xxx'


def failover(unhealthy_ec2):
    '''
    Remove the EIP from unhealthy instance then assign it to another server after doing health checks
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
        disassociate_status_code = disassociate_response['ResponseMetadata']['HTTPStatusCode']
        alloc_id = describe_response['Addresses'][0]['AllocationId']

        print('Disassociating {0} from {1}...'.format(eip, unhealthy_ec2))

        if disassociate_status_code == 200:
            associate_response = ec2.associate_address(
                InstanceId=healthy_ec2,
                AllocationId=alloc_id
            )

            print('Associating {0} to {1}...'.format(eip, healthy_ec2))
            return associate_response
        else:
            return disassociate_response
    except:
        raise


def check_eip(unhealthy_ec2):
    '''
    Check IP if it matches the Elastic IP before doing a failover
    '''
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        public_ip = ec2.Instance(unhealthy_ec2).public_ip_address

        if public_ip == eip:
            return failover(unhealthy_ec2)
        else:
            print('Nothing to do here.')
            sys.exit(0)
    except:
        raise


def main(event, context):
    alarm = event['Records'][0]['Sns']['Message']['AlarmName']
    state = event['Records'][0]['Sns']['Message']['NewStateValue']
    unhealthy_ec2 = event['Records'][0]['Sns']['Message']['Trigger']['Dimensions'][0]['value']

    print('Alarm:', alarm)
    print('State:', state)
    print(check_eip(unhealthy_ec2))
