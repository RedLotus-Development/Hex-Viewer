import os
import curses
import concurrent.futures

def hex_dump(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_bytes = ' '.join(f"{b:02x}" for b in chunk)
            ascii_bytes = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:08x}: {hex_bytes:<48}  |{ascii_bytes}|")
        return lines
    except Exception as e:
        return [f"Error reading file: {e}"]

def find_files(base_path, filter_pattern=""):
    base_path = os.path.expandvars(base_path)
    files = {}
    try:
        for entry in os.listdir(base_path):
            full_path = os.path.join(base_path, entry)
            if os.path.isfile(full_path):
                if filter_pattern:
                    if filter_pattern.lower() in entry.lower():
                        files[entry] = [full_path]
                else:
                    files[entry] = [full_path]
    except Exception as e:
        files["Error"] = [f"Error reading directory: {e}"]
    return files

def search_all_in_content(current_content, search_term):
    results = []
    for idx, line in enumerate(current_content):
        if search_term.lower() in line.lower():
            results.append((idx, line))
    return results

def display_ui(stdscr, files):
    curses.curs_set(0)
    mode = "file_selection"
    selected_file_index = 0
    current_content = []
    current_file_path = None
    load_future = None
    loaded_files = {}
    content_scroll = 0
    search_results = []
    search_scroll = 0
    search_selected_index = 0
    search_term = ""
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        if mode == "file_selection":
            stdscr.addstr(0, 2, "File Viewer - File Selection (Press Enter to view file)", curses.A_BOLD)
            file_names = list(files.keys())
            for idx, fname in enumerate(file_names):
                if idx == selected_file_index:
                    stdscr.addstr(2 + idx, 2, f"> {fname} <", curses.A_REVERSE)
                else:
                    stdscr.addstr(2 + idx, 2, f"  {fname}")
            stdscr.addstr(height - 1, 2, "Use UP/DOWN to select file, Enter to view, q to quit.")
        elif mode == "content_view":
            file_names = list(files.keys())
            selected_fname = file_names[selected_file_index]
            stdscr.addstr(0, 2, f"Viewing: {selected_fname} (Press '/' to search, 'b' to go back)", curses.A_BOLD)
            box_top = 2
            box_left = 2
            box_height = height - 4
            box_width = width - 4
            stdscr.attron(curses.A_BOLD)
            stdscr.box()
            stdscr.attroff(curses.A_BOLD)
            file_location = files[selected_fname][0]
            if current_file_path != file_location:
                current_file_path = file_location
                current_content = []
                load_future = None
                content_scroll = 0
            if current_file_path in loaded_files:
                current_content = loaded_files[current_file_path]
            else:
                if load_future is None:
                    load_future = executor.submit(hex_dump, current_file_path)
                if load_future and load_future.done():
                    current_content = load_future.result()
                    loaded_files[current_file_path] = current_content
                    load_future = None
            if not current_content:
                stdscr.addstr(box_top + (box_height // 2), box_left + 2, "Loading file, please wait...")
            else:
                max_lines = box_height - 2
                for i in range(max_lines):
                    line_index = content_scroll + i
                    if line_index < len(current_content):
                        line = current_content[line_index]
                        safe_line = line.replace('\x00', '')
                        stdscr.addstr(box_top + 1 + i, box_left + 1, safe_line[:box_width - 2])
            stdscr.addstr(height - 1, 2, "Use UP/DOWN or PgUp/PgDn to scroll, '/' to search, b to go back, q to quit.")
        elif mode == "search_results":
            stdscr.addstr(0, 2, f"Search results for: '{search_term}' (Enter to jump, 'b' to go back)", curses.A_BOLD)
            box_top = 2
            box_left = 2
            box_height = height - 4
            box_width = width - 4
            stdscr.attron(curses.A_BOLD)
            stdscr.box()
            stdscr.attroff(curses.A_BOLD)
            max_lines = box_height - 2
            for i in range(max_lines):
                result_index = search_scroll + i
                if result_index < len(search_results):
                    line_num, line_text = search_results[result_index]
                    display_text = f"Line {line_num:08x}: {line_text}"
                    if result_index == search_selected_index:
                        stdscr.addstr(box_top + 1 + i, box_left + 1, display_text[:box_width - 2], curses.A_REVERSE)
                    else:
                        stdscr.addstr(box_top + 1 + i, box_left + 1, display_text[:box_width - 2])
            stdscr.addstr(height - 1, 2, "Use UP/DOWN or PgUp/PgDn to navigate, Enter to jump, b to go back, q to quit.")
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            break
        if mode == "file_selection":
            if key == curses.KEY_UP and selected_file_index > 0:
                selected_file_index -= 1
            elif key == curses.KEY_DOWN and selected_file_index < len(files) - 1:
                selected_file_index += 1
            elif key in (10, 13):
                mode = "content_view"
                current_content = []
                load_future = None
                content_scroll = 0
        elif mode == "content_view":
            if key == curses.KEY_UP:
                if content_scroll > 0:
                    content_scroll -= 1
            elif key == curses.KEY_DOWN:
                if current_content and content_scroll < len(current_content) - ((height - 4) - 2):
                    content_scroll += 1
            elif key == curses.KEY_NPAGE:
                if current_content:
                    content_scroll = min(content_scroll + ((height - 4) - 2), max(len(current_content) - ((height - 4) - 2), 0))
            elif key == curses.KEY_PPAGE:
                if current_content:
                    content_scroll = max(content_scroll - ((height - 4) - 2), 0)
            elif key == ord('/'):
                stdscr.addstr(height - 2, 2, "Search: ")
                stdscr.clrtoeol()
                curses.echo()
                stdscr.refresh()
                try:
                    search_term = stdscr.getstr(height - 2, 10).decode('utf-8')
                except Exception:
                    search_term = ""
                curses.noecho()
                if search_term and current_content:
                    search_results = search_all_in_content(current_content, search_term)
                    if search_results:
                        mode = "search_results"
                        search_scroll = 0
                        search_selected_index = 0
                    else:
                        stdscr.addstr(height - 2, 2, "Not found. Press any key to continue.")
                        stdscr.getch()
            elif key == ord('b'):
                mode = "file_selection"
                current_content = []
                load_future = None
                content_scroll = 0
        elif mode == "search_results":
            if key == curses.KEY_UP:
                if search_selected_index > 0:
                    search_selected_index -= 1
                    if search_selected_index < search_scroll:
                        search_scroll = search_selected_index
            elif key == curses.KEY_DOWN:
                if search_selected_index < len(search_results) - 1:
                    search_selected_index += 1
                    max_lines = ((height - 4) - 2)
                    if search_selected_index >= search_scroll + max_lines:
                        search_scroll = search_selected_index - max_lines + 1
            elif key == curses.KEY_NPAGE:
                max_lines = ((height - 4) - 2)
                search_selected_index = min(search_selected_index + max_lines, len(search_results) - 1)
                search_scroll = min(search_scroll + max_lines, max(len(search_results) - max_lines, 0))
            elif key == curses.KEY_PPAGE:
                max_lines = ((height - 4) - 2)
                search_selected_index = max(search_selected_index - max_lines, 0)
                search_scroll = max(search_scroll - max_lines, 0)
            elif key in (10, 13):
                chosen_line_index, _ = search_results[search_selected_index]
                content_scroll = chosen_line_index
                mode = "content_view"
            elif key == ord('b'):
                mode = "content_view"
                search_results = []
                search_term = ""
    executor.shutdown(wait=False)

def main():
    base_path = input("Enter directory path (or leave blank for default '.minecraft'): ").strip()
    if not base_path:
        base_path = r"C:\Users\%username%\AppData\Roaming\.minecraft"
    filter_pattern = input("Enter filter pattern (or leave blank for all files): ").strip()
    files = find_files(base_path, filter_pattern)
    if not files:
        print("No files found.")
        return
    curses.wrapper(display_ui, files)

if __name__ == "__main__":
    main()