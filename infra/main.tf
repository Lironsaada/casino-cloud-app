resource "azurerm_resource_group" "casino" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "acr" {
  name                = "casinoregistry123"
  resource_group_name = azurerm_resource_group.casino.name
  location            = azurerm_resource_group.casino.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "casino-aks"
  location            = azurerm_resource_group.casino.location
  resource_group_name = azurerm_resource_group.casino.name
  dns_prefix          = "casinoapp"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}
