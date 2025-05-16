from pygls.lsp.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionParams,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
)

class CSSLanguageFeatures:
    def __init__(self):
        self.css_properties = [
            "color", "background-color", "margin", "padding", "font-size", 
            "font-weight", "display", "flex", "grid", "width", "height",
            "border", "text-align", "position", "top", "left", "right", "bottom"
        ]
    
    def on_document_open(self, ls, params: DidOpenTextDocumentParams):
        """Обработка события открытия CSS документа"""
        ls.show_message("Открыт CSS документ")
    
    def on_document_change(self, ls, params: DidChangeTextDocumentParams):
        """Обработка события изменения CSS документа"""
        pass
    
    def provide_completion(self, ls, params: CompletionParams) -> CompletionList:
        """Предоставление автодополнения для CSS"""
        # Возвращаем список CSS свойств
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=prop,
                    kind=CompletionItemKind.Property,
                    documentation=f"CSS свойство {prop}"
                )
                for prop in self.css_properties
            ]
        )