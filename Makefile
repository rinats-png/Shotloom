.PHONY: setup test demo-validate demo-compile demo-preflight doctor
setup:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
demo-validate:
	python -m shotloom.cli validate --project projects/night-protocol
demo-compile:
	python -m shotloom.cli compile --project projects/night-protocol --episode EP01
demo-preflight:
	python -m shotloom.cli preflight --project projects/night-protocol --episode EP01
doctor:
	python -m shotloom.cli doctor
