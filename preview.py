"""Read-only filename preview. Does not rename, copy, or delete user files."""
from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def plan(folder, prefix, start):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError('Select an existing folder.')
    if not prefix or prefix != prefix.strip() or re.search(r'[<>:"/\\|?*\x00-\x1f]', prefix):
        raise ValueError('Use a non-empty prefix without path separators or invalid Windows characters.')
    if not isinstance(start, int) or start < 0:
        raise ValueError('Starting number must be a non-negative integer.')
    files = sorted((p for p in folder.iterdir() if p.is_file() and not p.is_symlink()), key=lambda p: (p.name.casefold(), p.name))
    rows = []
    for number, source in enumerate(files, start):
        target = f'{prefix}_{number:03d}{source.suffix}'
        if len(target) > 240:
            raise ValueError('Generated filename is too long. Shorten the prefix.')
        rows.append((source.name, target))
    return rows


def main():
    root = tk.Tk()
    root.title('BatchRename - Read-only Preview')
    root.geometry('850x530')
    folder, prefix, start = tk.StringVar(), tk.StringVar(value='Product'), tk.StringVar(value='1')
    box = ttk.Frame(root, padding=18)
    box.pack(fill='both', expand=True)
    ttk.Label(box, text='STEP 1: PREVIEW ONLY', font=('Arial', 16, 'bold')).pack(anchor='w')
    ttk.Label(box, text='No files are renamed, copied or deleted. Subfolders and symbolic links are excluded.').pack(anchor='w', pady=8)
    ttk.Button(box, text='Select folder', command=lambda: folder.set(filedialog.askdirectory() or folder.get())).pack(anchor='w')
    ttk.Entry(box, textvariable=folder).pack(fill='x', pady=8)
    controls = ttk.Frame(box)
    controls.pack(fill='x')
    ttk.Label(controls, text='Prefix:').pack(side='left')
    ttk.Entry(controls, textvariable=prefix, width=24).pack(side='left', padx=8)
    ttk.Label(controls, text='Start:').pack(side='left')
    ttk.Entry(controls, textvariable=start, width=8).pack(side='left', padx=8)
    tree = ttk.Treeview(box, columns=('old','new'), show='headings')
    tree.heading('old', text='Original filename')
    tree.heading('new', text='Proposed filename')
    tree.pack(fill='both', expand=True, pady=12)
    status = tk.StringVar(value='Select sample_files to try the demo.')
    def preview():
        tree.delete(*tree.get_children())
        status.set('')
        try:
            rows = plan(folder.get(), prefix.get(), int(start.get()))
            for row in rows: tree.insert('', 'end', values=row)
            status.set(f'{len(rows)} files previewed. Original files unchanged.')
        except (ValueError, OSError) as exc:
            messagebox.showerror('Check your input', str(exc))
    ttk.Button(box, text='Preview names', command=preview).pack(anchor='w')
    ttk.Label(box, textvariable=status).pack(anchor='w', pady=8)
    root.mainloop()

if __name__ == '__main__':
    main()
