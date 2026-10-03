terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "flask_image" {
  name = "sample-flask-app:1.0"
}

resource "docker_container" "flask_instances" {
  count = 5
  name  = "flask-tf-${count.index}"
  image = docker_image.flask_image.image_id
  ports {
    internal = 5000
    external = 5100 + count.index
  }
}
