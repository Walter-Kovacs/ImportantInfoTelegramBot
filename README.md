# ImportantInfoTelegramBot

## Скрипт рвсклоадки из директории с кодом

леижит в [scripts/install/install.py](./srcipts/install/install.py)

### Описание интерфейса

формат запуска

```
python install.py < COMMAND > --arg1 --arg2
```

список и интерфейсы команд

#### COMMAND: install

```
python install.py install < --workdir=/path/to/install_dirr > <--source_code_dir=/path/to/dir/with/source_code > < --version=vesrion_string >
```

создаёт директорию `version` в директории `workdir`
и копирует туда файлы из `source_code_dir` ( устанавливает только файлы необходимые для работы сервиса, и файл requirements со списком зависимостей )
Подготавливает virtualenv в поддиректории `<workdir>/<version>/.venv`, сами зависимости не устанавливаются

#### COMMAND: enable

```
python install.py enable < --workdir=/path/to/install_dir > < --version=vesrion_string >
```

создаёт симлинк `<workdir>/bot`  указзывающий на `<workdir>/<vesrion>`. Если симлинк существовал, то переключает его, при этом в логах пишется куда указывал симлинк и куда стал указывать
пример лога команды
```
Enabling version from VERSION env var: 2023-08-30_08_02-deploy_script_upgrade-e9b167f; Just switching symlink, iibot service restart required after that
[INFO]: installation directory found: /usr/local/important_info_bot
[INFO]: redirecting symlink /usr/local/important_info_bot/bot: /usr/local/important_info_bot/2023-08-31_08_28-deploy_script_upgrade-9e95155 --> /usr/local/important_info_bot/2023-08-30_08_02-deploy_script_upgrade-e9b167f
```


#### COMMAND: show\_installed

```
python install.py show_installed < --workdir=/path/to/install_dir >
```

выводит список директорий (за исключением симлинка bot) в workdir. Список отсортирован по-убыванию лексикографически
Если на одну из директорий списка указывает симлинк `<workdir>/bot` она помечатеся звёздочкой
пример вывода:
```
root@c090780efd0d:/iibot# make show_installed
[INFO]: installation directory found: /usr/local/important_info_bot
[INFO]: Available versions in install_dir (/usr/local/important_info_bot):
	  2023-08-31_08_28-deploy_script_upgrade-9e95155
 	* 2023-08-30_08_02-deploy_script_upgrade-e9b167f
 	  2023-08-30_07_48-deploy_script_test-89bef92
 	  2023-03-25_10_30-deploy_script_test-2d8def1
 	  2023-03-08_13_14-deploy_script_test-81d8233
```

### Обёртка в Makefile

В Makefilе есть набор phony ресурсов использующий скрипт install.py для более удобной раскладки и отката

#### make deploy
- Пострлит переменную окружения (в окружении команды make) VERSION на основе времени текущего коммита, ветки, хеша текущего коммита.
- С помощью скрипта install.py cкопирует исходный код в директорию `/usr/local/important_info_bot/VERSION` и создаст virtualenv внутри
- Установит зависимости прописанные в файле requirements в virtualenv внутри директории `/usr/local/important_info_bot/VERSION/.venv`
- С помощью скрипта install.py переключит симлинк `/usr/local/important_info_bot/bot` на свежесозданную директорию `/usr/local/important_info_bot/VERSION`
- Выполнит команду `systemctl status iibot` (мы используем debian на сервере, ожидается что сервис iibot уже настроен)

#### make show\_installed
- С помощью скрипта install.py отображает список установленных версий в директории `/usr/local/important_info_bot`, помечает звёздочкой ту на которую указывает симлинк `/usr/local/important_info_bot/bot`, если звёздочки нет, значит симлинк не существует или указывает куда-то не туда.


#### VERSION=some\_vesrion make enable
- С помощью скрипта install.py переключает симлинк `/usr/loca/important_info_bot` на директорию `/usr/local/important_info_bot/VESRION`
Эта команда использует переменную окружения VERSION, если её не указать, она построит её самостоятельно так же как это делает `make deploy`

Предполагается что будет использоваться для отката бота.
Например, после очередного обновления `make deploy` мы видим что бот как-то поломался и нам нужно взять предыдущую стабильную версию.

Мы выполняем `make show_installed` и видим список версий, которые уже были нами установлены (предполагается что через `make deploy` поэтому в каждой из них уже есть установленные зависимости).
```
root@c090780efd0d:/iibot# make show_installed
[INFO]: installation directory found: /usr/local/important_info_bot
[INFO]: Available versions in install_dir (/usr/local/important_info_bot):
	  2023-08-30_08_02-deploy_script_upgrade-e9b167f
 	  2023-08-30_07_48-deploy_script_test-89bef92
 	  2023-03-08_13_14-deploy_script_test-81d8233
 	  2023-03-25_10_30-deploy_script_test-2d8def1
 	* 2023-08-31_08_28-deploy_script_upgrade-9e95155
```

Среди них есть как минимум одна стабильная на которой бот работал только что, копируем её название и выполняем `make enable`
```
VERSION=2023-08-30_07_48-deploy_script_test-89bef92 make enable
```
после чего нужно будет порелоадить iibot
```
systemctl reload iibot
```
