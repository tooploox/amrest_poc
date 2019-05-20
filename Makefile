.PHONY: clean lint test test-debug

#################################################################################
# DOCKER RELATED COMMANDS                                                       #
#################################################################################

IMAGE_NAME=amrest_poc
DATA_PATH=/home/datasets/backup/askorupa/data/
INSIDE_DATA_PATH=/data/amrest/

ifeq ($(PORT),)
	PORT=8000
endif

build:
	docker build -t $(USER)_$(IMAGE_NAME) .

dev:
	docker run --rm -ti -p $(PORT):$(PORT) \
    --name $(USER)_$(IMAGE_NAME)_dev \
    -v $(PWD)/:/project \
    -v /home/$(USER)/:/home \
    -v $(DATA_PATH):/data \
    -w="/project" \
    -e DATA_PATH=$(INSIDE_DATA_PATH) \
    $(USER)_$(IMAGE_NAME)

lab:
	docker run --rm -ti -p $(PORT):$(PORT) \
    --name $(USER)_$(IMAGE_NAME)_lab \
    -v $(PWD)/:/project \
    -v /home/$(USER)/:/home \
    -v $(DATA_PATH):/data \
    -w="/project" \
    -e DATA_PATH=$(INSIDE_DATA_PATH) \
	$(USER)_$(IMAGE_NAME) \
	jupyter lab --ip 0.0.0.0 --port $(PORT) --no-browser --allow-root

kill_dev:
	docker kill $(USER)_$(IMAGE_NAME)_dev; docker rm $(USER)_dev

kill_lab:
	docker kill $(USER)_$(IMAGE_NAME)_lab; docker rm $(USER)_lab

#################################################################################
# OTHER COMMANDS                                                                #
#################################################################################

clean:
	find . -name "__pycache__" -type d | xargs /bin/rm -rf
	rm -rf pytest_cache

lint:
	flake8 src

test:
	export PYTHONPATH=src; pytest

# Run tests but do not inhibit what's printed to stdout
test-debug:
	export PYTHONPATH=src; pytest -s
