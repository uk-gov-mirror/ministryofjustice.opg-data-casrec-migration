resource "aws_ecs_task_definition" "behat" {
  family                   = "behat-migration-${local.account.sirius_env}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 2048
  memory                   = 4096
  container_definitions    = "[${local.behat_migration}]"
  task_role_arn            = data.aws_iam_role.sirius_behat_task_role.arn
  execution_role_arn       = data.aws_iam_role.sirius_behat_execution_role.arn
  tags = merge(local.default_tags,
    { "Role" = "casrec-migration-${local.environment}" },
  )
}

locals {
  behat_migration = jsonencode({
    essential = true,
    image     = "${data.aws_ecr_repository.api_app.repository_url}:IN-553"
    command = [
      "php",
      "vendor/bin/behat",
      "--config=docker/behat_ci.yml",
      "--tags=@casrecmigration",
      "--colors",
      "-f",
      "pretty",
      "-o",
    "std"],
    name = "behat-migration-${local.account.sirius_env}",
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = aws_cloudwatch_log_group.casrec_migration.name,
        awslogs-region        = "eu-west-1",
        awslogs-stream-prefix = "casrec-migration-behat-${local.environment}"
      }
    },
    secrets     = local.sirius_api_secrets,
    environment = concat(local.sirius_shared_environment_variables, local.migration_env_vars)
  })
}

// data sources for sirius behat

//// we use this as workaround to get the sirius ids as they use name prefix...
//data "aws_ecs_task_definition" "sirius_behat_task" {
//    task_definition = "behat-v0-${local.account.sirius_env}"
//    depends_on = [ "aws_ecs_task_definition.sirius_behat_task" ]
//}

data "aws_iam_role" "sirius_behat_task_role" {
  name = "api-ecs-${local.account.sirius_env}-2020102109394774570000000c"
}

data "aws_iam_role" "sirius_behat_execution_role" {
  name = "execution-role-${local.account.sirius_env}-20201021093947635700000005"
}

data "aws_ecr_repository" "api_app" {
  name     = "sirius/api-app"
  provider = aws.management
}

data "aws_elasticsearch_domain" "sirius" {
  domain_name = "elasticsearch-${local.account.sirius_env}"
}

data "aws_secretsmanager_secret" "rds_api" {
  name = "rds-api-${local.account.name}"
}

data "aws_secretsmanager_secret" "jwt_key" {
  name = "${local.account.name}/jwt-key"
}

data "aws_secretsmanager_secret" "user_one_password" {
  name = "${local.account.name}/user-one-password"
}

data "aws_region" "current" {}

// Sirius Env Secrets
locals {
  sirius_api_secrets = [
    {
      name      = "OPG_CORE_BACK_USER_ONE_PASSWORD",
      valueFrom = data.aws_secretsmanager_secret.user_one_password.arn
    },
    {
      name      = "OPG_CORE_JWT_KEY",
      valueFrom = data.aws_secretsmanager_secret.jwt_key.arn
    },
    {
      name      = "OPG_CORE_BACK_DB_PASSWORD",
      valueFrom = data.aws_secretsmanager_secret.rds_api.arn
    },
  ]
}

// Sirius Env Vars
locals {
  sirius_shared_environment_variables = concat(
    [
      {
        name  = "OPG_CORE_BACK_FILESERVICE_URI"
        value = "http://file-service.${local.account.sirius_env}.ecs:8000/services/file-service"
      },
      {
        name  = "OPG_CORE_BACK_PDF_SERVICE"
        value = "http://pdf-service.${local.account.sirius_env}.ecs:80"
      },
      {
        name  = "OPG_CORE_BACK_CODE_GENERATOR",
        value = "https://dev.lpa-codes.api.opg.service.justice.gov.uk/v1"
      },
      {
        name  = "OPG_CORE_BACK_SQS_NOTIFY_QUEUE_URL",
        value = "https://sqs.eu-west-1.amazonaws.com/${local.account.account_id}/${local.account.sirius_env}-notify"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_28_DUE_DATE_PERIOD",
        value = "P60D"
      },
      {
        name  = "OPG_CORE_BACK_SQS_DDC_QUEUE_WAIT_TIME",
        value = "20"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_46_ACTIVE_DATE_PERIOD",
        value = "P35D"
      },
      {
        name  = "OPG_CORE_BACK_DB_USER",
        value = "opgcoreapi"
      },
      {
        name  = "OPG_SIRIUS_FEATURE_TOGGLE_PUBLIC_API",
        value = "1"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_22_DUE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_CORE_BACK_MEMBRANE_URI",
        value = "http://membrane.${local.account.sirius_env}.ecs"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_23_ACTIVE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_CORE_BACK_SQS_DDC_QUEUE_URL",
        value = "https://sqs.eu-west-1.amazonaws.com/${local.account.account_id}/${local.account.sirius_env}-ddc.fifo"
      },
      {
        name  = "OPG_CORE_BACK_FILE_PERSISTENCE_S3_BUCKET_NAME",
        value = "opg-backoffice-datastore-${local.account.sirius_env}"
      },
      {
        name  = "OPG_CORE_BACK_DDC_BACKEND_HOST",
        value = "api.${local.account.sirius_env}.ecs"
      },
      {
        name  = "OPG_CORE_BACK_DB_HOST",
        value = data.aws_rds_cluster.sirius.endpoint
      },
      {
        name  = "OPG_CORE_BACK_DB_READONLY_HOST",
        value = data.aws_rds_cluster.sirius.reader_endpoint
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_15_DUE_DATE_PERIOD",
        value = local.account.name == "development" ? "PT2M" : "P19D"
      },
      {
        name  = "OPG_CORE_BACK_ELASTICSEARCH_HOSTS",
        value = "${data.aws_elasticsearch_domain.sirius.endpoint}:80"
      },
      {
        name  = "OPG_CORE_BACK_SQS_ENDPOINT_URL",
        value = "https://sqs.${data.aws_region.current.name}.amazonaws.com"
      },
      {
        name  = "OPG_CORE_BACK_BACKEND_URI",
        value = "http://api.${local.account.sirius_env}.ecs"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_205_ACTIVE_DATE_PERIOD",
        value = "P18D"
      },
      {
        name  = "OPG_CORE_BACK_STATSD_PORT",
        value = "8125"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_47_DUE_DATE_PERIOD",
        value = "P20D"
      },
      {
        name  = "OPG_SIRIUS_SCHEDULER_USER",
        value = "opg+sirius@digital.justice.gov.uk"
      },
      {
        name  = "OPG_CORE_BACK_DDC_FILE_PERSISTENCE_S3_BUCKET_NAME",
        value = "opg-backoffice-jobsqueue-${local.account.sirius_env}"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_20_DUE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_23_DUE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_CORE_BACK_CASREC_EXPORT_S3_BUCKET_NAME",
        value = "opg-backoffice-casrec-exports-${local.account.sirius_env}"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_20_ACTIVE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_CORE_BACK_DB_NAME",
        value = data.aws_rds_cluster.sirius.database_name
      },
      {
        name  = "OPG_CORE_BACK_PUBLICAPI_S3_BUCKET_NAME",
        value = "opg-backoffice-public-api-${local.account.sirius_env}"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_47_ACTIVE_DATE_PERIOD",
        value = "P20D"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_28_ACTIVE_DATE_PERIOD",
        value = "P60D"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_16_DUE_DATE_PERIOD",
        value = local.account.name == "development" ? "PT2M" : "P20D"
      },
      {
        name  = "OPG_CORE_BACK_DB_PORT",
        value = tostring(data.aws_rds_cluster.sirius.port)
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_22_ACTIVE_DATE_PERIOD",
        value = "P10D"
      },
      {
        name  = "OPG_HELP_URL",
        value = "https://wordpress.dev"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_15_ACTIVE_DATE_PERIOD",
        value = local.account.name == "development" ? "PT2M" : "P19D"
      },
      {
        name  = "OPG_CORE_BACK_AWS_AUTH_TYPE",
        value = "iam"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_46_DUE_DATE_PERIOD",
        value = "P35D"
      },
      {
        name  = "OPG_CORE_BACK_AWS_DEBUG",
        value = "false"
      },
      {
        name  = "OPG_CORE_BACK_DISPLAY_EXCEPTIONS",
        value = "1"
      },
      {
        name  = "OPG_CORE_BACK_FRONTEND_URI",
        value = "http://frontend.${local.account.sirius_env}.ecs"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_205_DUE_DATE_PERIOD",
        value = "P18D"
      },
      {
        name  = "OPG_CORE_BACK_BUSINESS_RULES_TASK_16_ACTIVE_DATE_PERIOD",
        value = local.account.name == "development" ? "PT2M" : "P20D"
      },
      {
        name  = "PHP_FPM_MEMORY_LIMIT",
        value = "768M"
      },
  ], )
}

locals {
  migration_env_vars = [
    {
      name  = "BEHAT_PARAMS",
      value = "{\"extensions\" : {\"Behat\\\\GuzzleExtension\" : {\"base_url\" : \"http://api.${local.account.sirius_env}.ecs\"}}}"
  }]
}