.PHONY: start stop

start:
	sudo docker compose up --build -d --scale app=2
	sudo docker ps
	sudo docker compose logs

stop:
	sudo docker compose stop
