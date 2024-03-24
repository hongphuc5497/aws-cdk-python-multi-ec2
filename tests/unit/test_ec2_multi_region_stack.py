import os

import aws_cdk as cdk
import aws_cdk.assertions as assertions
from aws_cdk.assertions import Match

from ec2_multi_region.ec2_multi_region_stack import Ec2MultiRegionStack

def test_synthesizes_properly():
    app = cdk.App()

    # N.Virginia, Singapore, Frankfurt
    REGIONS = ['us-east-1', 'ap-southeast-1', 'eu-central-1']

    for region in REGIONS:
        stack = Ec2MultiRegionStack(
            app,
            f"Ec2MultiRegionStack-{region}",
            region=region,
            env=cdk.Environment(
                account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                region=region
            )
        )

        # Prepare the stack for assesrtion
        template = assertions.Template.from_stack(stack)

        # Assert the number of EC2 instance in the stack
        template.resource_count_is("AWS::EC2::Instance", 1)

