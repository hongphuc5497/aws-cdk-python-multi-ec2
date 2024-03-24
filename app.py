#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ec2_multi_region.ec2_multi_region_stack import Ec2MultiRegionStack

app = cdk.App()

# N.Virginia, Singapore, Frankfurt
REGIONS = ['us-east-1', 'ap-southeast-1', 'eu-central-1']

for region in REGIONS:
    Ec2MultiRegionStack(
        app,
        f"Ec2MultiRegionStack-{region}",
        region=region,
        env=cdk.Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=region
        )
    )

app.synth()
