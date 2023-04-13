![Yamdb workflow](https://github.com/AndrewNemz/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# yamdb_final

Учебный проект 16 спринта факультета бэкенд-разработки

### Технологии
- Python 3.7
- Django
- Docker
- Nginx

### Запуск проекта в dev-режиме
- Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/AndrewNemz/yamdb_final.git
cd api_yamdb/
```

- Установите и активируйте виртуальное окружение:
 ```
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
 ```
 
 - Установите зависимости из файла requirements.txt
  ```
pip install -r requirements.txt
 ```
 
 - Запустить приложение в контейнерах:
 
   из директории ```infra/```
   ```
   docker-compose up -d --build
   ```
   
  - Выполнить миграции:
 
    из директории ```infra/```
   
    ```
    docker-compose exec web python manage.py migrate
    ```
   
  - Собрать статику:
  
    из директории ```infra/```
    ```
    docker-compose exec web python manage.py collectstatic --no-input
    ```
    
   - Создать суперпользователя:
  
     из директории ```infra/```
     
     ```
     docker-compose exec web python manage.py createsuperuser
     ```
    
    
   - Остановить приложение в контейнерах:
  
      из директории ```infra/```
      
      ```
      docker-compose down -v
      ```


### Автор проекта:
    https://github.com/AndrewNemz

