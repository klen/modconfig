VERSION	?= minor

.PHONY: version
version:
	uv version --bump $(VERSION)
	git commit -am "build(version): $$(uv version --short)"
	git tag $$(uv version --short)
	git checkout master
	git pull
	git merge develop
	git checkout develop
	git push origin develop master
	git push --tags

.PHONY: minor
minor:
	make version VERSION=minor

.PHONY: patch
patch:
	make version VERSION=patch

.PHONY: major
major:
	make version VERSION=major


.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf


.PHONY: test
test:
	@uv run pytest tests.py


.PHONY: mypy
mypy:
	@uv run mypy modconfig


.PHONY: t
t:
	make test
