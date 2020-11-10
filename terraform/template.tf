data "aws_security_group" "sirius_ecs_api" {
  filter {
    name   = "tag:Name"
    values = ["api-ecs-${local.account.sirius_env}"]
  }
}

resource "local_file" "output" {
  content = templatefile("${path.module}/sirius_tasks.toml",
    {
      cluster            = local.account.sirius_env,
      sec_group          = data.aws_security_group.sirius_ecs_api.id,
      sec_group_membrane = data.aws_security_group.sirius_membrane.id,
      subnets            = join("\", \"", data.aws_subnet_ids.private.ids),
      account            = local.account.account_id
  })
  filename = "${path.module}/terraform.output.json"
}
