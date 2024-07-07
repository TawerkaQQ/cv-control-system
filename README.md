Устанавливаем qdrant docker image:
docker pull qdrant/qdrant

Первичный запуск контейнера с Qdrant:
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

Последующие запуски образа:
docker run -p 6333:6333 qdrant/qdrant 

Модуль db_creator - запускается 1 раз для создания базы данных Qdrant в директории. 
Модуль db_connector - Сверяет эмбеддинги с теми, что есть в БД и выводит 2 наиболее схожих результата.


Cоздание нового контейнера с postgres:
docker run -itd -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass_for_user -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data --name postgresql postgres


Создание новой бд в контейнере: 
docker exec -it postgresql env POSTGRES_USER=new_user POSTGRES_PASSWORD=pass_for_user

pgadmin:
docker run --name name -p 5050:80 -e "PGADMIN_DEFAULT_EMAIL=mail" -e "PGADMIN_DEFAULT_PASSWORD=pass" -d dpage/pgadmin4

