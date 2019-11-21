update-deps:
	pip install --upgrade pip-tools --user
	pip-compile --upgrade --output-file=- requirements/requires-install.in > requirements.txt
	pip-compile --upgrade --output-file=- requirements/requires-dev.in >> requirements.txt
	pip-compile --upgrade --output-file=- requirements/requires-testing.in >> requirements.txt

init:
	pip install --upgrade pip setuptools
	pip install --progress-bar off --no-cache-dir --editable .
	pip install --progress-bar off --no-cache-dir -r requirements.txt

build_renderer:
	@mkdir -p packages && \
	cd dash-renderer && \
	renderer build && \
	python setup.py sdist && \
	mv dist/* ../packages/ && cd ..

build_dcc:
	@mkdir -p packages && \
	git clone --depth 1 https://github.com/plotly/dash-core-components.git && \
	cd dash-core-components && \
	npm ci && npm run build && \
	python setup.py sdist && \
	mv dist/* ../packages/ && cd ..

build_test_renderer:
	@mkdir -p packages && \
	git clone --depth 1 https://github.com/plotly/dash-renderer-test-components && \
	cd dash-renderer-test-components && \
	npm ci && npm run build:all && \
	python setup.py sdist && \
	mv dist/* ../packages/ && cd ..

build_table:
	@mkdir -p packages && \
	git clone --depth 1 https://github.com/plotly/dash-table.git && \
	cd dash-table && \
	npm ci && npm run build && \
	python setup.py sdist && \
	mv dist/* ../packages/ && cd ..

build_html:
	@mkdir -p packages && \
	git clone --depth 1 https://github.com/plotly/dash-html-components.git && \
	cd dash-html-components && \
	npm ci && npm run build && \
	python setup.py sdist && \
	mv dist/* ../packages/ && cd ..

build_core: build_renderer build_dcc
build_misc: build_table build_html build_test_renderer
update: update-deps init

.PHONY: update-deps init update build_renderer build_dcc build_test_renderer build_core build_table build_html build_misc