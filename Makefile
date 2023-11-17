up:
	docker-compose up --build -d

down:
	docker-compose down

test:
	docker exec -it mobicult_trial_backend_1 python -m pytest