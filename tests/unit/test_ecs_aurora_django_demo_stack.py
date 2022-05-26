import aws_cdk as core
import aws_cdk.assertions as assertions

from ecs_aurora_django_demo.ecs_stack import ECSStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ecs_aurora_django_demo/ecs_aurora_django_demo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ECSStack(app, "ecs-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
