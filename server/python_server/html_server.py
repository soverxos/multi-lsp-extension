from pygls.lsp.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionParams,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    Position,
    Range,
    TextEdit,
)

class HTMLLanguageFeatures:
    def __init__(self):
        self.html_elements = [
            "div", "span", "p", "h1", "h2", "h3", "ul", "ol", "li", "table",
            "tr", "td", "th", "form", "input", "button", "a", "img", "header",
            "footer", "nav", "main", "section", "article"
        ]
    
    def on_document_open(self, ls, params: DidOpenTextDocumentParams):
        """Обработка события открытия HTML документа"""
        ls.show_message("Открыт HTML документ")
    
    def on_document_change(self, ls, params: DidChangeTextDocumentParams):
        """Обработка события изменения HTML документа"""
        pass
    
    def provide_completion(self, ls, params: CompletionParams) -> CompletionList:
        """Предоставление автодополнения для HTML"""
        document_uri = params.text_document.uri
        position = params.position
        
        # Получаем текст документа
        document = ls.workspace.get_document(document_uri)
        line = document.lines[position.line]
        
        # Проверяем, находимся ли мы в контексте тега
        before_cursor = line[:position.character]
        
        if "<" in before_cursor and ">" not in before_cursor.rsplit("<", 1)[1]:
            # Предлагаем HTML теги
            items = [
                CompletionItem(
                    label=element,
                    kind=CompletionItemKind.Snippet,
                    insert_text=f"{element}></{element}>",
                    documentation=f"HTML элемент {element}"
                )
                for element in self.html_elements
            ]
            return CompletionList(is_incomplete=False, items=items)
        
        # Если мы не в специальном контексте, возвращаем общий список тегов
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=element,
                    kind=CompletionItemKind.Class,
                    documentation=f"HTML элемент {element}"
                )
                for element in self.html_elements
            ]
        )