terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.78.0"
    }
  }
}

provider "google" {
  credentials = file("retail-dv-b374e702c563.json")
  project     = "retail-dv"
}