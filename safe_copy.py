"""Copy renamed files into a fresh output folder; never write to originals."""
from pathlib import Path
import os
import shutil
import stat
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from preview import plan


def copy_files(folder, prefix, start, output_parent, expected_rows=None):
    source = Path(folder).resolve(strict=True)
    parent = Path(output_parent).resolve(strict=True)
    if not parent.is_dir():
        raise ValueError('Select an existing output parent folder.')
    if parent == source or source in parent.parents:
        raise ValueError('Choose an output location outside the source folder.')
    rows = plan(source, prefix, start)
    if expected_rows is not None and rows != expected_rows:
        raise ValueError('The source file list changed. Preview again before copying.')
    if not rows:
        raise ValueError('There are no files to copy.')
    output = Path(tempfile.mkdtemp(prefix='BatchRename_', dir=parent))
    try:
        for old, new in rows:
            src = source / old
            if src.is_symlink() or not src.is_file():
                raise ValueError('A source file changed. Stop and preview again.')
            before = src.stat()
            with src.open('rb') as inp:
                opened = os.fstat(inp.fileno())
                if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                    raise ValueError('A source file changed during copying.')
                with (output / new).open('xb') as out:
                    shutil.copyfileobj(inp, out)
                after = os.fstat(inp.fileno())
            if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('A source file was edited during copying.')
        return output, len(rows)
    except Exception as exc:
        raise OSError(f'Copy did not finish. Originals were not modified. Partial copies may be in:\n{output}\n\n{exc}') from exc


def main():
    root = tk.Tk()
    root.title('BatchRename - Safe Copy')
    root.geometry('900x620')
    box = ttk.Frame(root, padding=18)
    box.pack(fill='both', expand=True)
    ttk.Label(box, text='STEP 2: SAFE COPY', font=('Arial', 16, 'bold')).pack(anchor='w')
    ttk.Label(box, text='Originals stay unchanged. Copies go into a new BatchRename_ folder.\nSubfolders and symbolic links are excluded. Copying large files may take time.').pack(anchor='w', pady=8)
    folder = tk.StringVar()
    prefix = tk.StringVar(value='Product')
    start = tk.StringVar(value='1')
    parent = tk.StringVar()
    status = tk.StringVar(value='Select sample_files, then choose an output location outside it.')
    reviewed = None
    for label, variable in [('Select source folder', folder), ('Select output location', parent)]:
        ttk.Button(box, text=label, command=lambda v=variable: v.set(filedialog.askdirectory(parent=root) or v.get())).pack(anchor='w')
        ttk.Entry(box, textvariable=variable).pack(fill='x', pady=5)
    controls = ttk.Frame(box)
    controls.pack(fill='x')
    for label, variable in [('Prefix:', prefix), ('Start:', start)]:
        ttk.Label(controls, text=label).pack(side='left')
        ttk.Entry(controls, textvariable=variable, width=24).pack(side='left', padx=8)
    tree = ttk.Treeview(box, columns=('old', 'new'), show='headings')
    tree.heading('old', text='Original filename')
    tree.heading('new', text='Copy filename')
    tree.pack(fill='both', expand=True, pady=12)
    def invalidate(*args):
        nonlocal reviewed
        reviewed = None
        copy_button.config(state='disabled')
        status.set('Settings changed. Click Preview names.')
    def preview():
        nonlocal reviewed
        invalidate()
        tree.delete(*tree.get_children())
        try:
            if not folder.get():
                raise ValueError('Select a source folder.')
            rows = plan(folder.get(), prefix.get(), int(start.get()))
            for row in rows:
                tree.insert('', 'end', values=row)
            reviewed = rows
            copy_button.config(state='normal' if rows else 'disabled')
            status.set(f'{len(rows)} files previewed. Originals unchanged.')
        except (ValueError, OSError) as exc:
            messagebox.showerror('Check your input', str(exc), parent=root)
    def copy():
        if reviewed is None:
            return
        if not parent.get():
            messagebox.showerror('Output location required', 'Choose an output location outside the source folder.', parent=root)
            return
        if not messagebox.askyesno('Create renamed copies?', f'Copy {len(reviewed)} files into a NEW folder under:\n{parent.get()}\n\nOriginal files will remain unchanged.', parent=root):
            return
        copy_button.config(state='disabled')
        try:
            output, count = copy_files(folder.get(), prefix.get(), int(start.get()), parent.get(), reviewed)
            status.set(f'{count} files copied. Originals unchanged.\n{output}')
            messagebox.showinfo('Copy complete', f'{count} files copied to:\n{output}\n\nOriginals unchanged.', parent=root)
        except (ValueError, OSError) as exc:
            messagebox.showerror('Copy stopped', str(exc), parent=root)
            status.set('Copy stopped. Read the error and preview again before retrying.')
    buttons = ttk.Frame(box)
    buttons.pack(fill='x')
    ttk.Button(buttons, text='Preview names', command=preview).pack(side='left')
    copy_button = ttk.Button(buttons, text='Create safe copies', command=copy, state='disabled')
    copy_button.pack(side='left', padx=12)
    ttk.Label(box, textvariable=status, wraplength=850).pack(anchor='w', pady=8)
    for variable in (folder, prefix, start, parent):
        variable.trace_add('write', invalidate)
    root.mainloop()

if __name__ == '__main__':
    main()
