import curses

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Press any key (press 'q' to quit)")
    while True:
        key = stdscr.getch()
        stdscr.clear()
        if key == ord('q'):
            break
        stdscr.addstr(0, 0, f"You pressed: {key}")
        stdscr.refresh()

curses.wrapper(main)