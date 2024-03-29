import os
from constructs import Construct

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
)

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "user_data.sh")
with open(file_path, "r") as f:
    user_data = f.read()

class Ec2MultiRegionStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        region: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lookup default VPC
        default_vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            is_default=True,
        )

        # Create Security Group to allow SSH
        custom_sg_base = CustomSecurityGroup(self, f"SecurityGroup_{region}", default_vpc)
        custom_sg_base.setup_lauch_wizard()
        custom_sg = custom_sg_base.sg

        # Create EC2
        my_instance = CustomEc2(self, f"EC2_{region}", default_vpc, custom_sg).instance

        CfnOutput(self,
            "Output",
            value=my_instance.instance_public_ip
        )


    def __str__(self) -> str:
        return f"{self.__class__.__name__} for {self.region}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for {self.region}"

class CustomVpc:
    def __init__(self, scope, id) -> None:
        self.vpc = ec2.Vpc(
            scope,
            id,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
        )

class CustomSecurityGroup:
    def __init__(self, scope, id, vpc) -> None:
        self.sg = ec2.SecurityGroup(
            scope,
            id,
            description="Security Group created from CDK",
            vpc=vpc,
            allow_all_outbound=True,
        )

    def setup_lauch_wizard(self):
        self.sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH from anywhere"
        )

        self.sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP from anywhere"
        )

        # self.sg.add_ingress_rule(
        #     ec2.Peer.any_ipv4(),
        #     ec2.Port.tcp(443),
        #     "Allow HTTPS from anywhere"
        # )


class CustomEc2:
    COMMON_INSTANCE_PROPS = {
        "instance_type": ec2.InstanceType.of(
            ec2.InstanceClass.T2,
            ec2.InstanceSize.MICRO
        ),
        "machine_image": ec2.MachineImage.latest_amazon_linux2(),
    }

    def __init__(self, scope, id, vpc, sg) -> None:
        self.instance = ec2.Instance(
            scope,
            id,
            vpc=vpc,
            security_group=sg,
            user_data=ec2.UserData.custom(user_data),
            **self.COMMON_INSTANCE_PROPS
        )

    def print_instance_info(self):
        print(f"Instance ID: {self.instance.instance_id}")
        print(f"Instance Public DNS: {self.instance.instance_public_dns_name}")
        print(f"Instance Public IP: {self.instance.instance_public_ip}")
        print(f"Instance Private IP: {self.instance.instance_private_ip}")
