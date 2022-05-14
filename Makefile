.PHONY: black
black:
	black -l 80 *.py
	black -l 80 app/*.py
	black -l 80 db/*.py
	black -l 80 webapp/*.py
