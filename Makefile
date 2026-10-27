run:
	@python3 main.py

clean:
	@find . -type d -name "__pycache__" -print -exec rm -rf {} +