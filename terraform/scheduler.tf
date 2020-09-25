resource "aws_iam_role" "etl_scheduled_tasks" {
  name               = "etl-scheduled-tasks-${terraform.workspace}"
  assume_role_policy = data.aws_iam_policy_document.events_assume.json
  tags               = local.default_tags
}

data "aws_iam_policy_document" "events_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "ecs_run_task_iam" {
  name   = "etl-run-task-${terraform.workspace}"
  role   = aws_iam_role.etl_scheduled_tasks.id
  policy = data.aws_iam_policy_document.events_run_task.json
}

data "aws_iam_policy_document" "events_run_task" {
  statement {
    sid       = "AllowPassRole"
    effect    = "Allow"
    actions   = ["iam:PassRole"]
    resources = ["*"]
  }

  statement {
    sid       = "AllowRunTask"
    effect    = "Allow"
    actions   = ["ecs:RunTask"]
    resources = ["*"]
  }
}

resource "aws_cloudwatch_event_rule" "etl_scheduler" {
  name                = "etl1-Scheduler-${terraform.workspace}"
  description         = "Execute the ETL1 Scheduler in ${terraform.workspace}"
  schedule_expression = "cron(00 03 * * ? *)"
}

resource "aws_cloudwatch_event_target" "etl1_scheduler" {
  target_id = "etl1-scheduler-${terraform.workspace}"
  arn       = aws_ecs_cluster.migration.arn
  rule      = aws_cloudwatch_event_rule.etl_scheduler.name
  role_arn  = aws_iam_role.etl_scheduled_tasks.arn

  ecs_target {
    launch_type         = "FARGATE"
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.etl1.arn
    network_configuration {
      subnets         = data.aws_subnet_ids.private.ids
      security_groups = [aws_security_group.etl.id]
    }
  }

  input = local.scheduler_overrides
}

locals {
  scheduler_overrides = jsonencode({
    containerOverrides = [{
      name    = "etl1-${terraform.workspace}",
      command = ["python3", "connect_db.py"]
    }]
  })
}
