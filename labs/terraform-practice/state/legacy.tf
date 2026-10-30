# A container someone started by hand, before Terraform knew about it:
#   docker run -d --name state-legacy -p 8112:80 nginx:1.30-alpine
#
# It was adopted with an import block like this one. After the apply that
# imported it, the block has no more work to do, so it was deleted.
#   import {
#     to = docker_container.legacy
#     id = "<the full ID from: docker inspect -f '{{.Id}}' state-legacy>"
#   }

resource "docker_container" "legacy" {
  name = "state-legacy"
  # Docker reports the image by the name used in `docker run`, so use the
  # name here too. The image ID would not match and force a replacement.
  image = docker_image.nginx.name

  ports {
    internal = 80
    external = 8112
  }

  # The Docker provider cannot read env or ports back from a running
  # container. Without this, the import plan says "must be replaced".
  lifecycle {
    ignore_changes = [env, ports]
  }
}
