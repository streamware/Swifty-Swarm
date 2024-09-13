locals {
  distributions = tolist(data.arvan_images.terraform_image.distributions)
  chosen_image = try(
    [for image in local.distributions : image
    if image.name == var.chosen_name && image.distro_name == var.chosen_distro_name][0],
    null
  )
  selected_plan = try([for plan in data.arvan_plans.plan_list.plans : plan if plan.id == var.chosen_plan_id][0], null)
  network_list = tolist(data.arvan_networks.terraform_network.networks)
  chosen_network = try(
    [for network in local.network_list : network
    if network.name == var.chosen_network_name],
    []
  )
}
