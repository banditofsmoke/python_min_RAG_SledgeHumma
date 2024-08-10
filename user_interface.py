import curses
import asyncio
from curses.textpad import Textbox, rectangle
import locale

# Set locale for proper Unicode handling
locale.setlocale(locale.LC_ALL, '')

def safe_addstr(stdscr, y, x, string, attr=0):
    height, width = stdscr.getmaxyx()
    if y < height and x < width:
        try:
            stdscr.addstr(y, x, string[:width-x-1], attr)
        except curses.error:
            pass

class AIThemedInterface:
    def __init__(self):
        self.menu_items = [
            "Add text document", "Add PDF document", "Search documents",
            "List all documents", "Record and transcribe audio", "Play audio",
            "List all audio files", "Delete document", "Delete audio file",
            "NLP mode", "Speech interaction mode", "Chatbot mode",
            "Advanced document management", "Exit"
        ]
        self.selected_item = 0

    def draw_menu(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = "Enhanced RAG System"
        safe_addstr(stdscr, 0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        # Draw menu items
        for idx, item in enumerate(self.menu_items):
            x = width // 4 if idx < len(self.menu_items) // 2 else 3 * width // 4
            y = 2 + (idx % (len(self.menu_items) // 2))
            if idx == self.selected_item:
                safe_addstr(stdscr, y, x - len(item) // 2 - 2, f"> {item} <", curses.color_pair(1) | curses.A_BOLD)
            else:
                safe_addstr(stdscr, y, x - len(item) // 2, item)
        
        # Draw AI-themed elements
        for i in range(height):
            safe_addstr(stdscr, i, 0, "█", curses.color_pair(3))
            safe_addstr(stdscr, i, width-1, "█", curses.color_pair(3))
        
        safe_addstr(stdscr, height-1, 0, "█" * width, curses.color_pair(3))
        safe_addstr(stdscr, height-2, 2, "Use arrow keys to navigate, Enter to select, 'q' to quit", curses.color_pair(4))

    async def run(self, stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

        while True:
            self.draw_menu(stdscr)
            stdscr.refresh()

            key = stdscr.getch()

            if key == ord('q'):
                return "Exit"
            elif key == curses.KEY_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif key == curses.KEY_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif key in [curses.KEY_ENTER, ord('\n')]:
                return self.menu_items[self.selected_item]

            # Debug information
            debug_info = f"Last key: {key}"
            safe_addstr(stdscr, stdscr.getmaxyx()[0]-1, 2, debug_info.ljust(stdscr.getmaxyx()[1]-3), curses.color_pair(4))

            await asyncio.sleep(0.1)

async def display_menu():
    interface = AIThemedInterface()
    return await curses.wrapper(interface.run)

async def show_message(stdscr, title, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    safe_addstr(stdscr, height//2 - 2, max(0, (width - len(title))//2), title, curses.A_BOLD)
    safe_addstr(stdscr, height//2, max(0, (width - len(message))//2), message)
    safe_addstr(stdscr, height//2 + 2, max(0, (width - 20)//2), "Press any key to continue")
    stdscr.refresh()
    stdscr.getch()

async def get_confirmation(stdscr, title, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    safe_addstr(stdscr, height//2 - 2, max(0, (width - len(title))//2), title, curses.A_BOLD)
    safe_addstr(stdscr, height//2, max(0, (width - len(message))//2), message)
    safe_addstr(stdscr, height//2 + 2, max(0, (width - 35)//2), "Press 'y' to confirm, any other key to cancel")
    stdscr.refresh()
    key = stdscr.getch()
    return key == ord('y')

async def get_input(stdscr, title, prompt):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    safe_addstr(stdscr, height//2 - 2, max(0, (width - len(title))//2), title, curses.A_BOLD)
    safe_addstr(stdscr, height//2, 2, prompt)
    editwin = curses.newwin(1, width-4, height//2+1, 2)
    rectangle(stdscr, height//2, 1, height//2+2, width-2)
    stdscr.refresh()

    box = Textbox(editwin)
    stdscr.refresh()
    box.edit()
    return box.gather().strip()

async def select_document(stdscr, documents, title):
    curses.curs_set(0)
    current_idx = 0
    start_idx = 0
    height, width = stdscr.getmaxyx()
    max_display = height - 4

    while True:
        stdscr.clear()
        safe_addstr(stdscr, 0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        for idx, doc in enumerate(documents[start_idx:start_idx+max_display], start=start_idx):
            if idx == current_idx:
                safe_addstr(stdscr, idx-start_idx+2, 2, f"> {doc['content'][:50]}...", curses.A_REVERSE)
            else:
                safe_addstr(stdscr, idx-start_idx+2, 2, f"  {doc['content'][:50]}...")

        safe_addstr(stdscr, height-1, 2, "Use arrow keys to navigate, Enter to select, 'q' to quit")
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q'):
            return None
        elif key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
            if current_idx < start_idx:
                start_idx = current_idx
        elif key == curses.KEY_DOWN and current_idx < len(documents) - 1:
            current_idx += 1
            if current_idx >= start_idx + max_display:
                start_idx = current_idx - max_display + 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            return documents[current_idx]

        await asyncio.sleep(0.1)

# Wrapper functions to use with asyncio.run()
async def show_message_wrapper(title, message):
    return await curses.wrapper(lambda stdscr: show_message(stdscr, title, message))

async def get_confirmation_wrapper(title, message):
    return await curses.wrapper(lambda stdscr: get_confirmation(stdscr, title, message))

async def get_input_wrapper(title, prompt):
    return await curses.wrapper(lambda stdscr: get_input(stdscr, title, prompt))

async def select_document_wrapper(documents, title):
    return await curses.wrapper(lambda stdscr: select_document(stdscr, documents, title))