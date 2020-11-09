resource "aws_ecr_repository" "registry" {
  name                 = "project_repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}