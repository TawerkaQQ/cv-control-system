# Всем привет, это наш совместный проект по детекции и идентификации людей с помощью веб-камеры, с фиксацией времени входа/выхода человека из здания

## Для того чтобы запустить проект выполните следующие действия: 

Устанавливаем qdrant docker image:

```bash
docker pull qdrant/qdrant
```

Первичный запуск контейнера с Qdrant:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

Последующие запуски образа:

```bash
docker run -p 6333:6333 qdrant/qdrant (запускать без venv)
```

**Модуль db_creator - запускается 1 раз для создания базы данных Qdrant в директории.**
**Модуль db_connector - Сверяет эмбеддинги с теми, что есть в БД и выводит 2 наиболее схожих результата.**

При скачивании реков может возникнуть ошибка: 

```bash
ImportError: cannot import name 'mesh_core_cython' from 'face3d.mesh.cython' (unknown location)
```

Для фикса сделать следующее: 

```bash
cd ./skb-access-control-system/python_package/insightface/thirdparty/face3d/mesh/cython
python3 setup.py build_ext --inplace
python3 setup.py install
```

Также для запуска нужно скачать модели по следующей [ссылке](https://drive.google.com/file/d/1qXsQJ8ZT42_xSmWIYy85IcidpiZudOCB/view).
После скачивания создаем папку **models/** и в нее распаковываем архив.

Для скачивания зависимостей:

```bash
pip3 install -r requirements.txt
```