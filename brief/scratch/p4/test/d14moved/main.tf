resource "docker_network" "app" {
  name = "p4-moved-net"
}

moved {
  from = docker_network.web
  to   = docker_network.app
}
