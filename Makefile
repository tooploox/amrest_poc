.PHONY: clean lint test test-debug

#################################################################################
# DOCKER RELATED COMMANDS                                                                #
#################################################################################

IMAGE_NAME=ds-campaign-cost-optimization
ifeq ($(PORT),)
	PORT=8000
endif

build:
	docker build -t $(IMAGE_NAME) .

dev:
	docker run --rm -ti -p $(PORT):$(PORT) \
    --name $(USER)_dev \
    -v $(PWD)/:/$(IMAGE_NAME) \
    -v $(G9_DATA_PATH):/data \
    -w="/$(IMAGE_NAME)" \
    -e GOOGLE_APPLICATION_CREDENTIALS=/data/$(IMAGE_NAME)/secrets/gcloud_credentials.json \
    -e G9_DATA_PATH=/data \
    -e PROJECT_NAME=$(IMAGE_NAME) \
    $(IMAGE_NAME)


lab:
	docker run --rm -ti -p $(PORT):$(PORT) \
    --name $(USER)_lab \
    -v $(PWD)/:/$(IMAGE_NAME) \
    -v $(G9_DATA_PATH):/data/ \
	-w="/$(IMAGE_NAME)" \
	-e GOOGLE_APPLICATION_CREDENTIALS=/data/$(IMAGE_NAME)/secrets/gcloud_credentials.json \
	-e G9_DATA_PATH=/data \
    -e PROJECT_NAME=$(IMAGE_NAME) \
	$(IMAGE_NAME) \
	jupyter lab --ip 0.0.0.0 --port $(PORT) --no-browser --allow-root


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
