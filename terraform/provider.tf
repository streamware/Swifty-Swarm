terraform {
  required_providers {
    arvan = {
      source = "terraform.arvancloud.ir/arvancloud/iaas"
    }
  }
}

provider "arvan" {
  api_key = "apikey b14ca5f4-272d-5f2a-b621-c26cef86c2dd"
}
