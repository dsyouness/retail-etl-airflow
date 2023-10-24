# Define variables
TERRAFORM_CONTAINER_NAME = terraform
TERRAFORM_PLAN_FILE = terraform.plan

# Targets
.PHONY: init plan apply

init:
	docker-compose -f docker-compose.override.yml run --rm terraform init

plan: init
	docker-compose -f docker-compose.override.yml run --rm terraform plan -out=$(TERRAFORM_PLAN_FILE)

apply: plan
	docker-compose -f docker-compose.override.yml run --rm terraform apply $(TERRAFORM_PLAN_FILE)
