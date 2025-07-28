package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/azure"
	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestTerraformAzureExample(t *testing.T) {
	t.Parallel()

	// Generate a random suffix for resource names
	uniqueID := random.UniqueId()
	
	// Construct the terraform options with default retryable errors to handle the most common retryable errors in terraform testing.
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		// The path to where our Terraform code is located
		TerraformDir: "../",

		// Variables to pass to our Terraform code using -var options
		Vars: map[string]interface{}{
			"resource_group_name": "casino-test-rg-" + uniqueID,
			"location":           "East US",
			"acr_name":           "casinotestacr" + uniqueID,
			"aks_cluster_name":   "casino-test-aks-" + uniqueID,
		},
	})

	// At the end of the test, run `terraform destroy` to clean up any resources that were created
	defer terraform.Destroy(t, terraformOptions)

	// This will run `terraform init` and `terraform apply` and fail the test if there are any errors
	terraform.InitAndApply(t, terraformOptions)

	// Run `terraform output` to get the value of an output variable
	resourceGroupName := terraform.Output(t, terraformOptions, "resource_group_name")
	acrLoginServer := terraform.Output(t, terraformOptions, "acr_login_server")
	aksClusterName := terraform.Output(t, terraformOptions, "aks_cluster_name")

	// Verify the resource group exists
	assert.True(t, azure.ResourceGroupExists(t, resourceGroupName, ""))

	// Verify the ACR exists
	assert.True(t, azure.ContainerRegistryExists(t, acrLoginServer, resourceGroupName, ""))

	// Verify the AKS cluster exists
	assert.True(t, azure.ManagedClusterExists(t, aksClusterName, resourceGroupName, ""))
}

func TestTerraformValidation(t *testing.T) {
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
	})

	// This will run `terraform init` and `terraform validate` and fail the test if there are any errors
	terraform.InitAndValidate(t, terraformOptions)
}

func TestTerraformPlan(t *testing.T) {
	uniqueID := random.UniqueId()
	
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../",
		Vars: map[string]interface{}{
			"resource_group_name": "casino-test-rg-" + uniqueID,
			"location":           "East US",
			"acr_name":           "casinotestacr" + uniqueID,
			"aks_cluster_name":   "casino-test-aks-" + uniqueID,
		},
		PlanFilePath: "../test.tfplan",
	})

	// This will run `terraform init` and `terraform plan` and fail the test if there are any errors
	terraform.InitAndPlan(t, terraformOptions)

	// Parse the plan file to verify expected resources
	plan := terraform.InitAndPlanAndShow(t, terraformOptions)
	
	// Verify that the plan includes the expected resources
	terraform.RequirePlannedValuesMapKeyExists(t, plan, "azurerm_resource_group.main")
	terraform.RequirePlannedValuesMapKeyExists(t, plan, "azurerm_container_registry.main")
	terraform.RequirePlannedValuesMapKeyExists(t, plan, "azurerm_kubernetes_cluster.main")
	terraform.RequirePlannedValuesMapKeyExists(t, plan, "azurerm_log_analytics_workspace.main")
} 