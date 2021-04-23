## Создание виртуальной машины из COI образа при помощи terraform
Отдельного метода в terraform нет, так как все данные для работы этого образа передаются в метадате.
Для корректной работы образа будем использовать заранее написанный docker-compose файл, который будем преобразовывать в формат, понимаемый API Yandex Cloud.
* Пишем корректный compose файл: 
``editor ./docker-compose.yaml``
  
* Преобразуем файл docker-compose.yaml в формат принимаемый terrafrom:
``bash ./convert.sh``
  
* Правим файл плана и запускаем создание машины: 
  ```
  editor ./main.tf
  terraform plan
  terraform apply
    ```