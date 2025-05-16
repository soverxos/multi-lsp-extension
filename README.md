# Multi-Language Server Extension for VSCode

Расширение Visual Studio Code с поддержкой нескольких языковых серверов на Python. Предоставляет интеллектуальное автодополнение для HTML, CSS и JSON файлов.

## Возможности

- **HTML автодополнение**: Поддержка стандартных HTML тегов и атрибутов
- **CSS автодополнение**: Предложения CSS свойств и значений
- **JSON автодополнение**: Сниппеты для работы с JSON объектами, массивами и свойствами

## Требования

- Visual Studio Code 1.67.0 или новее
- Python 3.7 или новее
- Node.js и npm

## Установка и использование

### Из исходного кода

1. Клонировать репозиторий:
   ```
   git clone https://github.com/soverxos/multi-lsp-extension.git
   cd multi-lsp-extension
   ```

2. Установить зависимости:
   ```
   npm install
   python -m pip install -r server/requirements.txt
   ```

3. Скомпилировать TypeScript:
   ```
   npm run compile
   ```

4. Запустить отладку (F5 в VS Code)

### Из marketplace (будет доступно позже)

1. Открыть VS Code
2. Перейти в раздел Extensions (Ctrl+Shift+X)
3. Найти "Multi Language Server Extension"
4. Нажать "Install"

## Как это работает

Расширение использует Language Server Protocol (LSP) для предоставления функций редактирования:

- Клиент на TypeScript интегрируется в VS Code
- Сервер на Python обрабатывает запросы автодополнения и другие языковые возможности
- Разные модули обрабатывают разные типы файлов

## Расширение функциональности

Чтобы добавить поддержку нового языка:

1. Создайте новый файл в `server/python_server/` (например, `javascript_server.py`)
2. Реализуйте класс с методами `on_document_open`, `on_document_change` и `provide_completion`
3. Добавьте новый обработчик в словарь `LANGUAGE_MODULES` в `main.py`
4. Обновите `documentSelector` в `extension.ts`

## Лицензия

[MIT](LICENSE)

## Автор

[Дмитрий Шевченко (SoverX)](https://github.com/soverxos)

## Вклад в проект

Вклад приветствуется! Пожалуйста, ознакомьтесь с [руководством по внесению вклада](CONTRIBUTING.md) (будет добавлено позже).