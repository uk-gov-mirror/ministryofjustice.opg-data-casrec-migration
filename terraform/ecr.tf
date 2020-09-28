locals {
  images = {
    etl1 = "${data.aws_ecr_repository.images["etl1"].repository_url}:${var.image_tag}"
    etl2 = "${data.aws_ecr_repository.images["etl2"].repository_url}:${var.image_tag}"
  }

  repositories = [
    "etl1",
    "etl2",
  ]
}

data "aws_ecr_repository" "images" {
  for_each = toset(local.repositories)

  name     = "casrec-migration/${each.key}"
  provider = aws.management
}
