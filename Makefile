IMAGE_NAME=household
DOCKERFILE_PATH=build/dockerfile
CONTAINER_NAME=household_container

HOST_PORT=5000
CONTAINER_PORT=5000

DOCKER_RUN_CMD=sudo docker run --rm -d --name $(CONTAINER_NAME) -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_NAME)

build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE_PATH) .

run:
	@echo "Running Docker container on port $(HOST_PORT)"
	$(DOCKER_RUN_CMD)

up: build run

stop:
	@echo "Stopping Docker container"
	sudo docker stop $(CONTAINER_NAME)

logs:
	@echo "Showing logs of Docker container"
	sudo docker logs $(CONTAINER_NAME)