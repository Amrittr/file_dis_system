# 🌐 Distributed File System (DFS) with Fault Tolerance

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Status](https://img.shields.io/badge/Status-Active-success)

A robust and scalable Distributed File System (DFS) simulator built in Python. This project demonstrates core distributed systems concepts including file chunking, replication, fault tolerance, and node failure recovery, all wrapped in an easy-to-use graphical user interface (GUI).

## ✨ Features

- **File Chunking & Distribution**: Automatically splits uploaded files into smaller manageable chunks (512 KB) and distributes them across multiple storage nodes.
- **Fault Tolerance & Replication**: Maintains data availability by replicating chunks across different nodes (Replication Factor: 2).
- **Heartbeat & Failure Detection**: Continuously monitors node health to detect simulated or real node failures.
- **Auto Re-replication**: Automatically recovers and re-replicates data from healthy nodes if a node failure is detected.
- **Interactive GUI**: User-friendly Tkinter-based interface to easily upload, download, and manage files.

## 📂 Project Structure

```text
dfs_project/
├── main.py                # Application entry point and Tkinter GUI implementation
├── dfs_engine.py          # Core logic for file chunking, distribution, and metadata management
├── fault_tolerance.py     # Heartbeat monitoring, node failure detection, and recovery logic
├── README.md              # Project documentation
└── dfs_storage/           # Simulated distributed storage nodes
    ├── node_1/
    ├── node_2/
    ├── node_3/
    └── metadata.json      # System state and chunk locations
```

## ⚙️ Configuration

The system is pre-configured with the following parameters:

| Setting | Value | Description |
| :--- | :--- | :--- |
| **CHUNK_SIZE** | 512 KB | The size of each data chunk. |
| **REPLICATION_FACTOR** | 2 | Number of copies for each chunk to ensure fault tolerance. |
| **num_nodes** | 3 | Total number of storage nodes in the simulated cluster. |

## 🚀 Getting Started

### Prerequisites

- **Python 3.8 or higher** is required.
- No external libraries are needed (only built-in modules like `os`, `json`, `shutil`, `threading`, and `tkinter`).

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Amrittr/file_dis_system.git
   cd file_dis_system
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 How to Use

1. **Start the System**: Run `python main.py` to launch the DFS interface.
2. **Upload a File**: Click **`Upload File`** and select any file from your local machine. The system will handle the chunking, distribution, and replication automatically.
3. **View Stored Files**: The uploaded files will appear in the `Stored Files` list.
4. **Download a File**: Select a file from the list, click **`Download File`**, choose a destination folder, and the system will reconstruct the file seamlessly.
5. **Observe Fault Tolerance** *(Optional)*: You can manually delete or modify chunks in `dfs_storage/node_X/` and see how the system logs warnings or automatically repairs missing chunks based on replication.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Amrittr/file_dis_system/issues).

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
