data "arvan_plans" "plan_list" {
  region = var.region
}

data "arvan_images" "terraform_image" {
  region     = var.region
  image_type = "distributions" // or one of: arvan, private
}

data "arvan_networks" "terraform_network" {
  region = var.region
}
