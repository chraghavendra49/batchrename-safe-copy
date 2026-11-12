# BatchRename Safe Copy

A Python desktop tool that previews new filenames and creates renamed copies in a separate folder while keeping original files unchanged.

## Features

- Preview original and proposed filenames.
- Choose a filename prefix and starting number.
- Preserve file contents and extensions.
- Create a new output folder for each copy operation.
- Reject invalid prefixes.
- Block output locations inside the source folder.
- Exclude subfolders and symbolic links.

## Requirements

- Python 3 with Tkinter.
- Tested on Windows with Python 3.13.
- No additional Python packages required.

This version requires Python; it is not a standalone executable.

## Download and Run

1. Download this repository using **Code → Download ZIP**.
2. Extract the ZIP.
3. Open the extracted project folder.
4. On Windows, double-click `START_SAFE_COPY.bat`.

Alternatively, open a terminal in the project folder and run:

```bash
python safe_copy.py
```

For the read-only preview app:

```bash
python preview.py
```

## How to Use

1. Click **Select source folder**.
2. Choose **Select output location**, using a location outside the source folder.
3. Enter a prefix such as `Product`.
4. Enter a starting number such as `10`.
5. Click **Preview names**.
6. Review the proposed filenames.
7. Click **Create safe copies** and confirm.

The app creates a new folder beginning with `BatchRename_` inside your chosen output location.

## Example

Using the included `sample_files` folder with prefix `Product` and starting number `10`:

| Original filename | Copied filename |
|---|---|
| sample_A.txt | Product_010.txt |
| sample_B.txt | Product_011.txt |
| తెలుగు.txt | Product_012.txt |

The original files remain in their source folder.

## Tests

Run from the project folder:

```bash
python -m unittest discover -v
```

Windows test result: **9 passed, 1 skipped, 0 failed**.
The symbolic-link test was skipped because the test environment could not create symbolic links.

Manual Windows checks covered:
- Filename previews and starting numbers.
- Successful copying and a sample text-content comparison.
- Preservation of original filenames.
- Separate output folders on repeated runs.
- Invalid-prefix rejection.
- Blocking the source folder as an output location.

## Limitations

- Processes only files directly inside the selected source folder.
- Does not process subfolders or symbolic links.
- Does not preserve filesystem timestamps or permissions.
- Large copies may temporarily make the window unresponsive.
- A failed operation may leave partial copies in the output folder identified by the error message.
- Avoid editing source files while copying.

Start with the included sample files before using your own files.

## Built With

Python, Tkinter, and Python's standard library.
