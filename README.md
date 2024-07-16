# MongoDB File Retriever

![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Python Version](https://img.shields.io/badge/python-3.x-blue)

MongoDB File Retriever is a graphical user interface (GUI) application for retrieving files stored in a MongoDB database. The application allows users to connect to a MongoDB instance, select a database and collection, and retrieve files by their Object ID.

## Features

- Connect to a MongoDB instance.
- Select a database and collection.
- List files stored in GridFS.
- Retrieve and save files to a specified directory.
- Copy file IDs and filenames to the clipboard.

## Requirements

- Python 3.x
- pymongo
- gridfs
- customtkinter
- tkinter

## Installation

### Clone the Repository

First, clone the repository:

```bash
git clone https://github.com/yourusername/MongoDB_file_retriever.git
cd MongoDB_file_retriever
```

## Usage
To start the application, run:

```bash
python mongodb_file_retriever.py
```

## GUI Instructions

1. **MongoDB URI**: Enter the MongoDB URI. The default is `mongodb://localhost:27017/`.
2. **Database and Collection**: Select the database and collection from the drop-down lists.
3. **List Files**: Click the "List Files" button to display files in the selected collection.
4. **Retrieve Files**: Select files and specify an output directory, then click the "Retrieve File(s)" button to download the files.

## Examples

**Example 1: Listing Files**

- Use the GUI to select a database and collection.
- Click the "List Files" button to display the files in the selected collection.

**Example 2: Retrieving Files**

- Use the GUI to select a database and collection.
- Click the "List Files" button to display the files in the selected collection.
- Select the files you want to retrieve.
- Specify an output directory.
- Click the "Retrieve File(s)" button to download the selected files to the specified directory.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) file for more details.

## Contribution

Contributions are welcome! Please ensure you follow the guidelines provided in the CONTRIBUTING.md file. For more information, see the LICENSE file.
