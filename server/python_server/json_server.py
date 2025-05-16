from pygls.lsp.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionParams,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    InsertTextFormat,
)

class JSONLanguageFeatures:
    def __init__(self):
        self.json_snippets = {
            "object": '{\n  "$1": "$2"\n}',
            "array": '[\n  "$1"\n]',
            "property": '"$1": "$2"',
        }
    
    def on_document_open(self, ls, params: DidOpenTextDocumentParams):
        """Обработка события открытия JSON документа"""
        ls.show_message("Открыт JSON документ")
    
    def on_document_change(self, ls, params: DidChangeTextDocumentParams):
        """Обработка события изменения JSON документа"""
        pass
    
    def provide_completion(self, ls, params: CompletionParams) -> CompletionList:
        """Предоставление автодополнения для JSON"""
        # Получаем документ и позицию курсора
        document = ls.workspace.get_document(params.text_document.uri)
        position = params.position
        
        items = []
        
        # Добавляем все доступные сниппеты с поддержкой подстановки
        for key, value in self.json_snippets.items():
            items.append(
                CompletionItem(
                    label=key,
                    kind=CompletionItemKind.Snippet,
                    documentation=f"JSON фрагмент: {key}",
                    insert_text=value,
                    insert_text_format=InsertTextFormat.Snippet,  # Важно для корректной работы сниппетов
                    sort_text=f"0_{key}"  # Для приоритета в списке автодополнения
                )
            )
            
        return CompletionList(is_incomplete=False, items=items)