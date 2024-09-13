variable "region" {
  type        = string
  description = "The chosen region for resources"
  default     = "ir-thr-ba1"
}

variable "chosen_distro_name" {
  type        = string
  description = "The chosen distro name for image"
  default     = "ubuntu"
}

variable "chosen_name" {
  type        = string
  description = "The chosen release for image"
  default     = "22.04"
}

variable "chosen_network_name" {
  type        = string
  description = "The chosen name of network"
  default     = "public216"
}

variable "chosen_plan_id" {
  type        = string
  description = "The chosen ID of plan"
  default     = "g4-8-2-0"
}
