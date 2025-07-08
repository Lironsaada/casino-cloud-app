variable "resource_group_name" {
  default = "casino-rg"
}

variable "location" {
  default = "East US"
}

variable "aks_cluster_name" {
  default = "casino-aks"
}

variable "acr_name" {
  default = "casinoregistry123"  # must be globally unique
}
