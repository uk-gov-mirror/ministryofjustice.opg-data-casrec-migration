resource "local_file" "output" {
  content = templatefile("${path.module}/sirius_tasks.toml",
    {
      cluster   = local.account.sirius_env,
      sec_group = tolist(data.aws_rds_cluster.sirius.vpc_security_group_ids)[0],
      subnets   = join("\", \"", data.aws_subnet_ids.private.ids),
      account   = local.account.account_id
  })
  filename = "${path.module}/terraform.output.json"
}
