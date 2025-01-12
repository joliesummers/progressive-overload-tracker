#!/usr/bin/env python3
from aws_cdk import (
    App,
    Stack,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_bedrock as bedrock,
    aws_iam as iam,
)
from constructs import Construct

class WorkoutTrackerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "WorkoutTrackerVPC", max_azs=2)

        # Create ECS Cluster
        cluster = ecs.Cluster(self, "WorkoutTrackerCluster", vpc=vpc)

        # Create RDS Instance
        database = rds.DatabaseInstance(
            self, "WorkoutTrackerDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,
            ),
        )

        # Create Bedrock access role
        bedrock_role = iam.Role(
            self, "BedrockAccessRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        bedrock_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )

        # Create Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WorkoutTrackerService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../backend"),
                container_port=8000,
                task_role=bedrock_role
            ),
        )

        # Add environment variables
        fargate_service.task_definition.default_container.add_environment(
            "DATABASE_URL", f"postgresql://postgres:postgres@{database.instance_endpoint.hostname}/workout_tracker"
        )

        # Allow access from ECS to RDS
        database.connections.allow_default_port_from(fargate_service.service)

app = App()
WorkoutTrackerStack(app, "WorkoutTrackerStack")
app.synth()
