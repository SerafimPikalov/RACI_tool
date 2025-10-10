.PHONY: enrich serve

enrich:
	python scripts/enrich_raci.py

serve:
	python -m http.server 8003
