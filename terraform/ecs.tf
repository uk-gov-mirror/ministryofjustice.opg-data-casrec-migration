resource "aws_ecs_cluster" "migration" {
  name = "casrec-migration-${local.environment}"
  tags = local.default_tags
}

resource "aws_ecs_task_definition" "etl1" {
  family                   = "etl1-${terraform.workspace}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 2048
  memory                   = 4096
  container_definitions    = "[${local.etl1}]"
  task_role_arn            = aws_iam_role.etl1.arn
  execution_role_arn       = aws_iam_role.execution_role.arn
  tags = merge(local.default_tags,
    { "Role" = "casrec-migration-${local.environment}" },
  )
}

locals {
  etl1 = jsonencode({
    cpu       = 0,
    essential = true,
    image     = local.images.etl1,
    name      = "etl1",
    healthCheck = {
      command     = ["CMD-SHELL", "echo hello || exit 1"],
      startPeriod = 30,
      interval    = 15,
      timeout     = 10,
      retries     = 3
    },
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = aws_cloudwatch_log_group.casrec_migration.name,
        awslogs-region        = "eu-west-1",
        awslogs-stream-prefix = "casrec-migration-${local.environment}"
      }
    },
    secrets = [
      {
        name      = "DB_PASSWORD",
        valueFrom = aws_secretsmanager_secret.casrec_migration.arn
      },
    ],
    environment = [
      {
        name  = "DB_HOST",
        value = aws_rds_cluster.cluster_serverless.endpoint
      },
      {
        name  = "DB_PORT",
        value = tostring(aws_rds_cluster.cluster_serverless.port)
      },
      {
        name  = "DB_NAME",
        value = aws_rds_cluster.cluster_serverless.database_name
      },
      {
        name  = "DB_USER",
        value = aws_rds_cluster.cluster_serverless.master_username
      },
      {
        name  = "ENVIRONMENT",
        value = terraform.workspace
      },
    ]
  })
}

resource "aws_cloudwatch_log_group" "casrec_migration" {
  name              = "casrec-migration-${local.environment}"
  retention_in_days = 180
  tags              = local.default_tags
}

//EXECUTION ROLES

resource "aws_iam_role" "execution_role" {
  name               = "migration-execution-role.${local.environment}"
  assume_role_policy = data.aws_iam_policy_document.execution_role_assume_policy.json
  tags               = local.default_tags
}

data "aws_iam_policy_document" "execution_role_assume_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role_policy" "execution_role" {
  policy = data.aws_iam_policy_document.execution_role.json
  role   = aws_iam_role.execution_role.id
}

data "aws_iam_policy_document" "execution_role" {
  statement {
    effect    = "Allow"
    resources = ["*"]

    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "ssm:GetParameters",
      "secretsmanager:GetSecretValue",
    ]
  }
}

//TASK ROLE

resource "aws_iam_role" "etl1" {
  assume_role_policy = data.aws_iam_policy_document.task_role_assume_policy.json
  name               = "casrec-migration.${local.environment}"
  tags               = local.default_tags
}

data "aws_iam_policy_document" "task_role_assume_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "ecs_task_s3" {
  statement {
    effect    = "Allow"
    resources = ["*"]

    actions = [
      "s3:GetObject",
      "s3:ListObjectVersions",
      "s3:ListBucketVersions",
      "s3:GetObjectTagging",
      "s3:ListObjects",
      "s3:ListBucket"
    ]
  }
}

resource "aws_iam_role_policy" "etl_task_s3" {
  name   = "casrec-migration-task-logs.${local.environment}"
  policy = data.aws_iam_policy_document.ecs_task_s3.json
  role   = aws_iam_role.etl1.id
}

// SECURITY GROUP
resource "aws_security_group" "etl" {
  name_prefix = "casrec-migration-ecs-${terraform.workspace}-"
  vpc_id      = data.aws_vpc.sirius.id
  description = "ETL1 ECS task"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    local.default_tags,
    map("Name", "etl1-ecs-${terraform.workspace}")
  )
}

//REPLACE THIS AND LOCK DOWN
resource "aws_security_group_rule" "etl_to_all_egress" {
  type              = "egress"
  protocol          = "-1"
  from_port         = 0
  to_port           = 0
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.etl.id
  description       = "Outbound ETL"
}

resource "aws_security_group_rule" "etl_to_db_egress" {
  type                     = "egress"
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
  source_security_group_id = aws_security_group.etl.id
  security_group_id        = aws_security_group.db.id
}
