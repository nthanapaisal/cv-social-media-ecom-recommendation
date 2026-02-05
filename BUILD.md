
Conda:
    1. source ~/miniconda3/bin/activate             
    2. conda create -n cv-ecomm-rec-api python=3.11 -y
    3. conda activate cv-ecomm-rec-api
    4. pip install -r requirements.txt
    5. uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
        1. to kill process run: kill -9 $(lsof -ti :8000)
        2. Endpoints - http://localhost:8000/docs

Docker: 
    1. cd cv-social-media-ecom-recommendation
    2. docker build -t cv-ecomm-rec-api .
    3. docker run -p 127.0.0.1:8000:8000 cv-ecomm-rec-api
    4. Endpoints - http://127.0.0.1:8000/docs
    5. ctrl+c not needed since you can build and overwrite previous image with same name but clean up process
            1 check running containers: docker ps -a
            2 stop running and remove manually: docker rm -f <container_id>
            3 check images: docker images
            4 remove image to free up space in your machine: docker rmi cv-ecomm-rec-api

Docker Compose: 
    1. cd cv-social-media-ecom-recommendation
    2. docker compose up --build
        Endpoints - http://127.0.0.1:8000/docs
    3. ctrl + c and choose one below
        1. stop+remove containers, but keep image and volume: docker compose down
        2. OR stop and delete containers and images: docker compose down --rmi all
        3. OR stop and delete EVERYTHING + volume: docker compose down --rmi all --volumes