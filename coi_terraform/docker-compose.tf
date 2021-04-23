variable "docker-compose" {
  default = "version: '3.7'\nservices:\n  myapp:\n    container_name: myapp\n    image: cr.yandex/crp*******/myapp:2021-01-01\n    network_mode: 'host'\n    restart: always"
}
