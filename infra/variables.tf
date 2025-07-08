variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "casino-rg"
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "westeurope"
}
