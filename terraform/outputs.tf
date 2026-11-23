output "repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.my_app.repository_url
}