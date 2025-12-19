@echo off
chcp 65001 >nul
echo ========================================
echo Транслятор конфигурационного языка
echo Автоматическая установка и тестирование
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

echo [1/5] Проверка Python... OK
echo.

:: Создание виртуального окружения
if not exist "venv" (
    echo [2/5] Создание виртуального окружения...
    python -m venv venv
    echo Виртуальное окружение создано!
) else (
    echo [2/5] Виртуальное окружение уже существует
)
echo.

:: Активация виртуального окружения
echo [3/5] Активация окружения...
call venv\Scripts\activate.bat
echo.

:: Установка зависимостей
echo [4/5] Установка зависимостей...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)
echo Зависимости установлены!
echo.

:: Создание директории для вывода
if not exist "output" mkdir output

:: Запуск тестов
echo [5/5] Запуск тестов...
echo ----------------------------------------
pytest -v --tb=short
if errorlevel 1 (
    echo.
    echo [ВНИМАНИЕ] Некоторые тесты не прошли!
    echo.
) else (
    echo.
    echo [УСПЕХ] Все тесты прошли успешно!
    echo.
)

:: Демонстрация работы
echo ========================================
echo Демонстрация работы транслятора
echo ========================================
echo.

echo Пример 1: Конфигурация БД
python -m src.cli -i examples/database_config.txt -o output/database.yaml
if errorlevel 1 (
    echo [ОШИБКА] при обработке database_config.txt
) else (
    echo [OK] database.yaml создан
)
echo.

echo Пример 2: Конфигурация веб-сервера
python -m src.cli -i examples/web_server_config.txt -o output/webserver.yaml
if errorlevel 1 (
    echo [ОШИБКА] при обработке web_server_config.txt
) else (
    echo [OK] webserver.yaml создан
)
echo.

echo Пример 3: Игровые настройки
python -m src.cli -i examples/game_settings.txt -o output/game.yaml
if errorlevel 1 (
    echo [ОШИБКА] при обработке game_settings.txt
) else (
    echo [OK] game.yaml создан
)
echo.

echo ========================================
echo Готово! Результаты в папке output/
echo ========================================
echo.
echo Для просмотра результатов:
echo   - output/database.yaml
echo   - output/webserver.yaml  
echo   - output/game.yaml
echo.

pause