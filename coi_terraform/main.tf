locals {
  user = "username"
  service_account_key_file = "key.json"
  folder_id = "b1g********"
  cloud_id = "b1g*********"
  zone = "ru-central1-a"
}

provider "yandex" {
  service_account_key_file = local.service_account_key_file
  folder_id = local.folder_id
  cloud_id = local.cloud_id
  zone = local.zone
}

data "yandex_vpc_subnet" "main-subnet-b" {
  subnet_id = "e2l***"
}

data "yandex_compute_image" "coi-image" {
  family = "container-optimized-image"
}

resource "yandex_compute_disk" "bootdisk-public" {
  size = 10
  type = "network-ssd"
  zone = var.zone-b
  image_id = data.yandex_compute_image.coi-image.id
}

resource "yandex_compute_instance" "publicvm" {
  name = "coi-vm"
  platform_id = "standard-v2"
  zone = var.zone-b
  service_account_id = "aje****"
  metadata = {
    user-data = var.userdata-linux
    serial-port-enable = "0"
    docker-compose = var.docker-compose
  }
  boot_disk {
    disk_id = yandex_compute_disk.bootdisk-public.id
  }
  network_interface {
    subnet_id = data.yandex_vpc_subnet.main-subnet-b.id
  }
  resources {
    cores = 2
    core_fraction = "100"
    memory = 4
  }
}
