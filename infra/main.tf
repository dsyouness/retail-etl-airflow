# terraform to create bucket in gcs
resource "google_storage_bucket" "bucket" {
  name          = "retail-dsy"
  location      = "EU"
  force_destroy = true
}
# terraform to create dataset in bigquery
resource "google_bigquery_dataset" "dataset" {
  dataset_id    = "retail"
  friendly_name = "Retail Dataset"
  description   = "Retail Dataset"
  location      = "EU"
}
# terraform to create table in bigquery
resource "google_bigquery_table" "country" {
  dataset_id = "retail"
  table_id   = "country"
  schema     = <<EOF
  [
    {
      "name": "id",
      "type": "INT64"
    },
    {
      "name": "iso",
      "type": "STRING"
    },
    {
      "name": "name",
      "type": "STRING"
    },
    {
      "name": "nicename",
      "type": "STRING"
    },
    {
      "name": "iso3",
      "type": "STRING"
    },
    {
      "name": "numcode",
      "type": "INT64"
    },
    {
      "name": "phonecode",
      "type": "INT64"
    }]
  EOF
}