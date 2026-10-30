resource "docker_network" "app" {
  name = "p4-life-net"

  lifecycle {
    prevent_destroy = false
  }
}
