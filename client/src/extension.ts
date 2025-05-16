import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';
import { workspace, ExtensionContext, window, ProgressLocation, commands, OutputChannel } from 'vscode';

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from 'vscode-languageclient/node';

let client: LanguageClient;
let outputChannel: OutputChannel;

async function checkPythonDependencies(context: ExtensionContext): Promise<boolean> {
  const requirementsPath = context.asAbsolutePath(path.join('server', 'requirements.txt'));
  const pythonCommand = workspace.getConfiguration('python').get<string>('pythonPath') || 'python';

  try {
    // Проверка наличия pygls
    const testCommand = `${pythonCommand} -c "import pygls; print('success')"`;
    try {
      cp.execSync(testCommand);
      return true;
    } catch (err) {
      // Если импорт pygls не удался, нужно установить зависимости
      const installButton = 'Установить';
      const response = await window.showInformationMessage(
        'Необходимо установить зависимости для языкового сервера. Установить сейчас?',
        installButton, 'Отмена'
      );
      
      if (response !== installButton) {
        return false;
      }
      
      return await window.withProgress({
        location: ProgressLocation.Notification,
        title: 'Установка зависимостей для Python-сервера...',
        cancellable: false
      }, async () => {
        return new Promise<boolean>((resolve) => {
          const installCommand = `${pythonCommand} -m pip install -r ${requirementsPath}`;
          cp.exec(installCommand, (error, stdout, stderr) => {
            if (error) {
              window.showErrorMessage(`Ошибка при установке зависимостей: ${stderr}`);
              resolve(false);
            } else {
              window.showInformationMessage('Зависимости успешно установлены!');
              resolve(true);
            }
          });
        });
      });
    }
  } catch (err) {
    window.showErrorMessage(`Ошибка при проверке зависимостей: ${err}`);
    return false;
  }
}

export async function activate(context: ExtensionContext) {
  outputChannel = window.createOutputChannel('Multi Language Server');
  outputChannel.appendLine('Инициализация многоязычного сервера...');
  
  // Регистрируем команды
  context.subscriptions.push(
    commands.registerCommand('multiLanguageServer.restart', async () => {
      if (client) {
        await client.stop();
        outputChannel.appendLine('Сервер остановлен, перезапуск...');
        startServer(context);
      }
    })
  );
  
  context.subscriptions.push(
    commands.registerCommand('multiLanguageServer.showOutput', () => {
      outputChannel.show();
    })
  );
  
  // Проверяем, включен ли сервер в настройках
  const config = workspace.getConfiguration('multiLanguageServer');
  if (!config.get<boolean>('enable', true)) {
    outputChannel.appendLine('Языковой сервер отключен в настройках');
    return;
  }
  
  // Проверяем зависимости Python перед запуском сервера
  const dependenciesOk = await checkPythonDependencies(context);
  
  if (!dependenciesOk) {
    window.showErrorMessage('Расширение не может быть активировано без необходимых зависимостей.');
    return;
  }
  
  startServer(context);
}

function startServer(context: ExtensionContext) {
  const config = workspace.getConfiguration('multiLanguageServer');
  
  // Путь к скрипту сервера
  const serverPath = context.asAbsolutePath(
    path.join('server', 'python_server', 'main.py')
  );

  // Получаем путь к Python из настроек расширения или из настроек Python
  let pythonPath = config.get<string>('pythonPath');
  if (!pythonPath) {
    pythonPath = workspace.getConfiguration('python').get<string>('pythonPath') || 'python';
  }

  outputChannel.appendLine(`Используется интерпретатор Python: ${pythonPath}`);

  // Формируем аргументы для сервера
  const args = [serverPath, '--stdio'];
  
  // Передаем настройки для включения/отключения языков
  if (!config.get<boolean>('html.enable', true)) {
    args.push('--disable-html');
  }
  
  if (!config.get<boolean>('css.enable', true)) {
    args.push('--disable-css');
  }
  
  if (!config.get<boolean>('json.enable', true)) {
    args.push('--disable-json');
  }
  
  if (!config.get<boolean>('notifications', true)) {
    args.push('--disable-notifications');
  }

  // Опции сервера
  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: args,
    options: {
      env: {
        ...process.env,
        PYTHONPATH: context.asAbsolutePath('server')
      }
    }
  };

  // Опции для клиента языкового сервера
  const clientOptions: LanguageClientOptions = {
    // Регистрируем языки, которые будем обрабатывать
    documentSelector: [
      { scheme: 'file', language: 'html' },
      { scheme: 'file', language: 'css' },
      { scheme: 'file', language: 'json' },
    ],
    synchronize: {
      // Уведомление сервера об изменении конфигурации
      configurationSection: ['multiLanguageServer'],
      fileEvents: workspace.createFileSystemWatcher('**/.clientrc')
    },
    outputChannel: outputChannel
  };

  // Создание клиента языкового сервера
  client = new LanguageClient(
    'multiLanguageServer',
    'Multi Language Server',
    serverOptions,
    clientOptions
  );

  // Запуск клиента. Это также запускает сервер
  client.start();
  
  if (config.get<boolean>('notifications', true)) {
    window.showInformationMessage('Многоязычный сервер активирован!');
  }
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}