TARGET = nurdpaste
VERSION = latest

CONTAINER_TAG = $(TARGET):$(VERSION)

all: build

build:
	buildah build \
		-f Dockerfile \
		--tag $(CONTAINER_TAG) \
		--no-cache \
		--squash \
		--omit-history \
		--force-rm \
		.

clean:
	buildah images | awk '/nurdpaste/{ print $$3 }' | while read IMAGE_ID; do \
	  buildah rmi $${IMAGE_ID}; \
	done
