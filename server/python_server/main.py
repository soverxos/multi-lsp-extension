#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

from pygls.server import LanguageServer
from pygls.lsp.methods import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_COMPLETION,
    INITIALIZE
)
from pygls.lsp.types import (
    CompletionList,
    CompletionItem,
    CompletionOptions,
    CompletionParams,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    InitializeParams,
    InitializeResult,
    MessageType,
    ServerCapabilities,
    TextDocumentSyncKind,
)

from html_server import HTMLLanguageFeatures
from css_server import CSSLanguageFeatures
from json_server import JSONLanguageFeatures

class MultiLanguageServer(LanguageServer):
    def __init__(self, disabled_languages=None, show_notifications=True):
        super().__init__()
        self.disabled_languages = disabled_languages or []
        self.show_notifications = show_notifications
        
        # Инициализируем используемые языковые модули
        self.language_handlers = {}
        
        if 'html' not in self.disabled_languages:
            self.language_handlers.update({
                ".html": HTMLLanguageFeatures(),
                ".htm": HTMLLanguageFeatures(),
            })
        
        if 'css' not in self.disabled_languages:
            self.language_handlers.update({
                ".css": CSSLanguageFeatures(),
            })
        
        if 'json' not in self.disabled_languages:
            self.language_handlers.update({
                ".json": JSONLanguageFeatures(),
            })

    def get_language_handler(self, uri: str) -> Any:
        """Определяет обработчик на основе расширения файла"""
        path = Path(uri.replace("file://", "", 1))
        extension = path.suffix.lower()
        return self.language_handlers.get(extension)

    def show_message_if_enabled(self, message: str, message_type: MessageType = MessageType.Info):
        """Показывает сообщение только если уведомления включены"""
        if self.show_notifications:
            self.show_message(message, message_type)

def initialize_server(disabled_languages=None, show_notifications=True):
    server = MultiLanguageServer(disabled_languages, show_notifications)
    
    @server.feature(INITIALIZE)
    def initialize(ls: MultiLanguageServer, params: InitializeParams) -> InitializeResult:
        """Инициализация сервера с поддержкой нескольких языков"""
        ls.show_message_if_enabled("Сервер инициализируется...")
        
        # Выводим информацию о включенных языках
        enabled_languages = []
        if 'html' not in ls.disabled_languages:
            enabled_languages.append("HTML")
        if 'css' not in ls.disabled_languages:
            enabled_languages.append("CSS")
        if 'json' not in ls.disabled_languages:
            enabled_languages.append("JSON")
            
        ls.show_message_if_enabled(f"Включенные языки: {', '.join(enabled_languages)}")
        
        return InitializeResult(
            capabilities=ServerCapabilities(
                text_document_sync=TextDocumentSyncKind.INCREMENTAL,
                completion_provider=CompletionOptions(
                    trigger_characters=['.', '<', '"', "'", "/"]
                ),
            )
        )

    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: MultiLanguageServer, params: DidOpenTextDocumentParams):
        """Обработка события открытия документа"""
        document_uri = params.text_document.uri
        handler = ls.get_language_handler(document_uri)
        
        if handler:
            ls.show_message_if_enabled(f"Обработка {document_uri} с использованием {handler.__class__.__name__}")
            handler.on_document_open(ls, params)
        else:
            path = Path(document_uri.replace("file://", "", 1))
            extension = path.suffix.lower()
            if extension in [".html", ".htm", ".css", ".json"] and any(ext in ls.disabled_languages for ext in ["html", "css", "json"]):
                ls.show_message_if_enabled(f"Поддержка для {extension} отключена в настройках", MessageType.Warning)
            else:
                ls.show_message_if_enabled(f"Для {document_uri} не найден обработчик", MessageType.Warning)

    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: MultiLanguageServer, params: DidChangeTextDocumentParams):
        """Обработка события изменения документа"""
        document_uri = params.text_document.uri
        handler = ls.get_language_handler(document_uri)
        
        if handler:
            handler.on_document_change(ls, params)

    @server.feature(TEXT_DOCUMENT_COMPLETION)
    def completion(ls: MultiLanguageServer, params: CompletionParams) -> CompletionList:
        """Обработка запроса автодополнения"""
        document_uri = params.text_document.uri
        handler = ls.get_language_handler(document_uri)
        
        if handler:
            return handler.provide_completion(ls, params)
        
        return CompletionList(is_incomplete=False, items=[])
        
    return server

def main():
    parser = argparse.ArgumentParser(description='Сервер поддержки нескольких языков для VS Code')
    parser.add_argument('--stdio', action='store_true', help='использовать stdio')
    parser.add_argument('--disable-html', action='store_true', help='отключить поддержку HTML')
    parser.add_argument('--disable-css', action='store_true', help='отключить поддержку CSS')
    parser.add_argument('--disable-json', action='store_true', help='отключить поддержку JSON')
    parser.add_argument('--disable-notifications', action='store_true', help='отключить уведомления')
    
    args = parser.parse_args()
    
    # Формируем список отключенных языков
    disabled_languages = []
    if args.disable_html:
        disabled_languages.append('html')
    if args.disable_css:
        disabled_languages.append('css')
    if args.disable_json:
        disabled_languages.append('json')
        
    # Создаём сервер
    server = initialize_server(
        disabled_languages=disabled_languages,
        show_notifications=not args.disable_notifications
    )
    
    if args.stdio:
        server.start_io()
    else:
        server.show_message("Этот сервер поддерживает только stdio коммуникацию", MessageType.Error)
        sys.exit(1)

if __name__ == '__main__':
    main()