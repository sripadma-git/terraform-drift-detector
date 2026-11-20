output "ec2_instance_id" {
  description = "ID of the Terraform Drift Detector EC2 instance"
  value       = aws_instance.drift_detector.id
}

output "ec2_instance_type" {
  description = "Configured EC2 instance type"
  value       = aws_instance.drift_detector.instance_type
}

output "security_group_id" {
  description = "ID of the dedicated security group"
  value       = aws_security_group.drift_detector.id
}

output "availability_zone" {
  description = "Availability zone of the EC2 instance"
  value       = aws_instance.drift_detector.availability_zone
}
