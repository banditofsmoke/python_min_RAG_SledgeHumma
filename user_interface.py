from prompt_toolkit import Application
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.application import get_app
from config import ITEMS_PER_PAGE

def select_document(documents, title):
    selected_index = [0]
    page = [0]
    search_query = ['']
    sort_by = ['timestamp']
    sort_order = ['desc']
    exit_flag = [False]

    def get_formatted_text():
        result = []
        result.append(('bold', f"{title}\n\n"))
        
        filtered_docs = [doc for doc in documents if search_query[0].lower() in doc['content'].lower()]
        filtered_docs.sort(key=lambda x: x[sort_by[0]], reverse=(sort_order[0] == 'desc'))
        
        start = page[0] * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        current_page_docs = filtered_docs[start:end]
        
        for i, doc in enumerate(current_page_docs, start=start):
            if i == selected_index[0]:
                result.append(('reverse', f"> {doc['timestamp']}: {doc['content'][:50]}... [{doc.get('category', 'N/A')}]\n"))
            else:
                category_color = {
                    'default': '',
                    'important': '#ansired',
                    'personal': '#ansigreen',
                    'work': '#ansiblue'
                }.get(doc.get('category', 'default'), '')
                result.append((category_color, f"  {doc['timestamp']}: {doc['content'][:50]}... [{doc.get('category', 'N/A')}]\n"))
        
        result.append(('', f"\nPage {page[0] + 1}/{(len(filtered_docs) - 1) // ITEMS_PER_PAGE + 1}"))
        result.append(('', "\nPress 'q' to return to main menu"))
        return result

    def update_search(text):
        search_query[0] = text
        page[0] = 0
        selected_index[0] = 0

    search_field = TextArea(
        height=1,
        prompt='Search: ',
        multiline=False,
        wrap_lines=False,
        accept_handler=update_search
    )

    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        selected_index[0] = (selected_index[0] - 1) % len(documents)

    @kb.add('down')
    def _(event):
        selected_index[0] = (selected_index[0] + 1) % len(documents)

    @kb.add('pageup')
    def _(event):
        page[0] = max(0, page[0] - 1)

    @kb.add('pagedown')
    def _(event):
        page[0] = min((len(documents) - 1) // ITEMS_PER_PAGE, page[0] + 1)

    @kb.add('enter')
    def _(event):
        event.app.exit()

    @kb.add('q')
    def _(event):
        exit_flag[0] = True
        event.app.exit()

    @kb.add('c-d')
    def _(event):
        if 0 <= selected_index[0] < len(documents):
            documents.pop(selected_index[0])
            selected_index[0] = min(selected_index[0], len(documents) - 1)

    @kb.add('c-e')
    def _(event):
        if 0 <= selected_index[0] < len(documents):
            doc = documents[selected_index[0]]
            new_content = input(f"Edit document content (current: {doc['content']}): ")
            if new_content:
                doc['content'] = new_content

    @kb.add('c-s')
    def _(event):
        nonlocal sort_by, sort_order
        sort_options = ['timestamp', 'content', 'category']
        current_index = sort_options.index(sort_by[0])
        sort_by[0] = sort_options[(current_index + 1) % len(sort_options)]
        if sort_by[0] != sort_options[current_index]:
            sort_order[0] = 'desc'
        else:
            sort_order[0] = 'asc' if sort_order[0] == 'desc' else 'desc'

    root_container = HSplit([
        search_field,
        Window(content=FormattedTextControl(get_formatted_text)),
    ])

    layout = Layout(root_container)

    application = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True
    )

    application.run()
    
    if exit_flag[0]:
        return None
    return documents[selected_index[0]]

def display_menu():
    print("\n1. Add text document")
    print("2. Add PDF document")
    print("3. Search documents")
    print("4. List all documents")
    print("5. Record and transcribe audio")
    print("6. Play audio")
    print("7. List all audio files")
    print("8. Delete document")
    print("9. Delete audio file")
    print("10. NLP mode")
    print("11. Speech interaction mode")
    print("12. Chatbot mode")
    print("13. Exit")
    return input("Enter your choice: ")