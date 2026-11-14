variable "resource_group_name" {
  type = string
}

variable "cluster_name" {
  type    = string
  default = "headlines-aks"
}

variable "vm_size" {
  type    = string
  default = "Standard_B2s"
}
