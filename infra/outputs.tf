output "resource_group_name" {
  value = azurerm_resource_group.casino.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "kube_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}
