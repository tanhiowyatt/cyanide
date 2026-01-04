.PHONY: test run clean install

test:
	mkdir -p logs/logs_tests
	pytest --cov=src --cov=honeypot tests/integration -v 2>&1 | tee logs/logs_tests/test_output.log

run:
	python3 honeypot.py > logs/server/stdout.log 2>&1 & uvicorn web.app:app --host 0.0.0.0 --port 8000 > logs/server/dashboard.log 2>&1

install:
	pip install -r requirements.txt

clean:
	rm -f server.log dashboard.log
