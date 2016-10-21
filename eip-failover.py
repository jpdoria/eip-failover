import boto3
import sys

is_ok = 'running'
region = 'us-east-1'
instances = ['i-12345678', 'i-87654321']
eip = '51.23.123.123'


def failover(public_ip, instance):
    '''
    Assign the EIP to another server after doing health checks
    '''
    try:
        ec2 = boto3.client('ec2', region_name=region)
        describe_response = ec2.describe_addresses(
            PublicIps=[
                public_ip
            ]
        )
        assoc_id = describe_response['Addresses'][0]['AssociationId']
        disassociate_response = ec2.disassociate_address(
            AssociationId=assoc_id
        )
        disassociate_status_code = disassociate_response['ResponseMetadata']['HTTPStatusCode']
        alloc_id = describe_response['Addresses'][0]['AllocationId']

        print('Disassociating {}...'.format(public_ip))

        if disassociate_status_code == 200:
            associate_response = ec2.associate_address(
                InstanceId=instance,
                AllocationId=alloc_id
            )

            print('Associating {0} to {1}...'.format(public_ip, instance))

            associate_status_code = associate_response['ResponseMetadata']['HTTPStatusCode']

            if associate_status_code == 200:
                return True
    except:
        raise


def health_check():
    '''
    Perform health checks
    '''
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        (a, b, c, d) = (None,)*4

        for instance in instances:
            print('Checking {}...'.format(instance))

            state = ec2.Instance(instance).state
            public_ip = ec2.Instance(instance).public_ip_address

            if (state['Name'] == is_ok) and (public_ip == eip):
                a = 'check_a'
                print('{} is alive and it\'s using the Elastic IP!!!'.format(instance))

            elif (state['Name'] == is_ok) and (public_ip != eip):
                b = 'check_b'
                print('{} is alive and it\'s not using the Elastic IP.'.format(instance))

            elif (state['Name'] != is_ok) and (public_ip != eip):
                c = 'check_c'
                print('{} is dead and it\'s not using the Elastic IP.'.format(instance))

            elif (state['Name'] != is_ok) and (public_ip == eip):
                d = 'check_d'
                print('{} is dead and it\'s using the Elastic IP!!!'.format(instance))

        if (a and c):
            print('WARNING: one proxy server is dead')
            sys.exit(1)
        elif (a and d):
            print('Two instances using the same EIP?')
            sys.exit(1)
        elif (b and c) or (c and d):
            print('CRITICAL: PROXY SERVERS ARE DEAD!!!')
            sys.exit(2)
        elif (b and d):
            instances.remove(instance)
            failover(public_ip, instances[0])
    except:
        raise


def main(event, context):
    health_check()

    if True:
        print('OK')
    else:
        raise
