# Docker Storage & Network Assignment

## Q1: Docker Storage
- Demonstrated container-layer data loss: data written inside a container was lost after the container was deleted and a new one was started.
- Demonstrated persistence using a named volume (`mydata`): data written in one container was still accessible after that container was deleted and a new container was attached to the same volume.
- Demonstrated persistence using a bind mount (`~/docker-lab/bind-demo`): a host folder was mounted into a container; changes made inside the container appeared on the host file (`hostfile.txt`) and persisted after container deletion.

## Q2: Docker Network
- Created a custom bridge network (`my-network`) and attached two containers (`container1`, `container2`) to it.
- Verified communication between containers using container **names** (Docker's built-in DNS) via `ping container2` from `container1`.
- Verified communication using container **IP addresses** directly, obtained via `docker inspect`.
