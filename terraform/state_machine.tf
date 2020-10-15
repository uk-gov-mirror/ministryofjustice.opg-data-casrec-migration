resource "aws_iam_role" "state_machine" {
  assume_role_policy = data.aws_iam_policy_document.state_assume.json
  name               = "casrec-mig-state-machine.${local.environment}"
  tags               = local.default_tags
}

data "aws_iam_policy_document" "state_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["states.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "state_machine" {
  statement {
    effect    = "Allow"
    resources = [aws_iam_role.etl1.arn, aws_iam_role.execution_role.arn]
    actions = [
      "iam:GetRole",
      "iam:PassRole"
    ]
  }
  statement {
    effect    = "Allow"
    resources = ["arn:aws:ecs:eu-west-1:${local.account.account_id}:task-definition/etl1-${terraform.workspace}*"]
    actions   = ["ecs:RunTask"]
  }
  statement {
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "ecs:StopTask",
      "ecs:DescribeTasks"
    ]
  }
  statement {
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule"
    ]
  }
  statement {
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets"
    ]
  }
}

resource "aws_iam_role_policy" "state_machine" {
  name   = "casrec-mig-state.${local.environment}"
  policy = data.aws_iam_policy_document.state_machine.json
  role   = aws_iam_role.state_machine.id
}

locals {
  subnets_string = join(",", [for s in data.aws_subnet_ids.private.ids : format("%q", s)])
}

resource "aws_sfn_state_machine" "casrec_migration" {
  name     = "casrec-mig-state-machine"
  role_arn = aws_iam_role.state_machine.arn

  definition = <<EOF
{
    "StartAt": "Parrallel ETL1",
    "States": {
        "Parrallel ETL1": {
            "Type": "Parallel",
            "End": true,
            "Branches": [
                {
                    "StartAt": "Run ETL1 task1",
                    "States": {
                        "Run ETL1 task1": {
                            "Type": "Task",
                            "Resource": "arn:aws:states:::ecs:runTask.sync",
                            "Parameters": {
                                "LaunchType": "FARGATE",
                                "Cluster": "${aws_ecs_cluster.migration.arn}",
                                "TaskDefinition": "${aws_ecs_task_definition.etl1.arn}",
                                "NetworkConfiguration": {
                                    "AwsvpcConfiguration": {
                                        "Subnets": [${local.subnets_string}],
                                        "SecurityGroups": ["${aws_security_group.etl.id}"],
                                        "AssignPublicIp": "DISABLED"
                                    }
                                },
                                "Overrides": {
                                    "ContainerOverrides": [{
                                        "Name": "etl1",
                                        "Command": ["python3", "casrec_load.py"]
                                    }]
                                }
                            },
                            "End": true
                        }
                    }
                },
                {
                    "StartAt": "Run ETL1 task2",
                    "States": {
                        "Run ETL1 task2": {
                            "Type": "Task",
                            "Resource": "arn:aws:states:::ecs:runTask.sync",
                            "Parameters": {
                                "LaunchType": "FARGATE",
                                "Cluster": "${aws_ecs_cluster.migration.arn}",
                                "TaskDefinition": "${aws_ecs_task_definition.etl1.arn}",
                                "NetworkConfiguration": {
                                    "AwsvpcConfiguration": {
                                        "Subnets": [${local.subnets_string}],
                                        "SecurityGroups": ["${aws_security_group.etl.id}"],
                                        "AssignPublicIp": "DISABLED"
                                    }
                                },
                                "Overrides": {
                                    "ContainerOverrides": [{
                                        "Name": "etl1",
                                        "Command": ["python3", "casrec_load.py"]
                                    }]
                                }
                            },
                            "End": true
                        }
                    }
                }
            ]
        }
    }
}
EOF
}
