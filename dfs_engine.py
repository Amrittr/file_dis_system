import hashlib
import json
import os
import shutil
from typing import Dict, List, Optional

CHUNK_SIZE = 512 * 1024  # 512 KB
REPLICATION_FACTOR = 2


class DFSEngine:
    def __init__(self, base_dir: str = "dfs_storage", num_nodes: int = 3):
        self.base_dir = base_dir
        self.num_nodes = num_nodes
        self.nodes = [f"node_{i+1}" for i in range(self.num_nodes)]
        self.metadata_path = os.path.join(self.base_dir, "metadata.json")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        for node in self.nodes:
            os.makedirs(os.path.join(self.base_dir, node), exist_ok=True)
        if not os.path.exists(self.metadata_path):
            self._write_metadata({})

    def _read_metadata(self) -> Dict:
        if not os.path.exists(self.metadata_path):
            return {}
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_metadata(self, data: Dict) -> None:
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _healthy_nodes(self, failed_nodes: Optional[List[int]]) -> List[int]:
        failed_nodes = failed_nodes or []
        return [i for i in range(self.num_nodes) if i not in failed_nodes]

    def upload_file(self, file_path: str, failed_nodes: Optional[List[int]] = None) -> Dict:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path)

        healthy = self._healthy_nodes(failed_nodes)
        if len(healthy) < REPLICATION_FACTOR:
            raise RuntimeError("Not enough healthy nodes to satisfy replication.")

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        metadata = self._read_metadata()
        chunks_meta = []

        with open(file_path, "rb") as f:
            chunk_index = 0
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                checksum = hashlib.md5(data).hexdigest()
                chunk_id = f"{file_name}.chunk_{chunk_index}"

                start_idx = chunk_index % len(healthy)
                assigned = []
                for r in range(REPLICATION_FACTOR):
                    node_id = healthy[(start_idx + r) % len(healthy)]
                    assigned.append(node_id)
                    node_dir = os.path.join(self.base_dir, self.nodes[node_id])
                    chunk_path = os.path.join(node_dir, chunk_id)
                    with open(chunk_path, "wb") as cf:
                        cf.write(data)

                chunks_meta.append(
                    {
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_index,
                        "checksum": checksum,
                        "nodes": assigned,
                        "size": len(data),
                    }
                )
                chunk_index += 1

        metadata[file_name] = {
            "file_size": file_size,
            "num_chunks": len(chunks_meta),
            "chunks": chunks_meta,
        }
        self._write_metadata(metadata)
        return metadata[file_name]

    def download_file(
        self, file_name: str, output_path: str, failed_nodes: Optional[List[int]] = None
    ) -> bool:
        metadata = self._read_metadata()
        if file_name not in metadata:
            return False

        healthy = self._healthy_nodes(failed_nodes)
        if not healthy:
            return False

        file_meta = metadata[file_name]
        chunks = sorted(file_meta["chunks"], key=lambda c: c["chunk_index"])
        output_file = os.path.join(output_path, file_name)

        try:
            with open(output_file, "wb") as out:
                for chunk in chunks:
                    chunk_ok = False
                    for node_id in chunk["nodes"]:
                        if node_id not in healthy:
                            continue
                        node_dir = os.path.join(self.base_dir, self.nodes[node_id])
                        chunk_path = os.path.join(node_dir, chunk["chunk_id"])
                        if not os.path.exists(chunk_path):
                            continue
                        with open(chunk_path, "rb") as cf:
                            data = cf.read()
                        if hashlib.md5(data).hexdigest() != chunk["checksum"]:
                            continue
                        out.write(data)
                        chunk_ok = True
                        break
                    if not chunk_ok:
                        return False
        except OSError:
            return False

        return True

    def rereplicate(self, failed_node_id: int, failed_nodes: Optional[List[int]] = None) -> int:
        metadata = self._read_metadata()
        healthy = self._healthy_nodes(failed_nodes or [failed_node_id])
        if not healthy:
            return 0

        moved = 0
        for file_name, file_meta in metadata.items():
            for chunk in file_meta["chunks"]:
                if failed_node_id not in chunk["nodes"]:
                    continue

                source_node = None
                for node_id in chunk["nodes"]:
                    if node_id in healthy:
                        source_node = node_id
                        break
                if source_node is None:
                    continue

                target_node = None
                for node_id in healthy:
                    if node_id not in chunk["nodes"]:
                        target_node = node_id
                        break
                if target_node is None:
                    continue

                src_dir = os.path.join(self.base_dir, self.nodes[source_node])
                dst_dir = os.path.join(self.base_dir, self.nodes[target_node])
                src_path = os.path.join(src_dir, chunk["chunk_id"])
                dst_path = os.path.join(dst_dir, chunk["chunk_id"])
                if os.path.exists(src_path):
                    shutil.copyfile(src_path, dst_path)
                    chunk["nodes"] = [
                        target_node if n == failed_node_id else n for n in chunk["nodes"]
                    ]
                    moved += 1

        self._write_metadata(metadata)
        return moved

    def get_node_stats(self) -> List[Dict]:
        stats = []
        for idx, node in enumerate(self.nodes):
            node_dir = os.path.join(self.base_dir, node)
            chunk_files = []
            total_size = 0
            if os.path.exists(node_dir):
                for name in os.listdir(node_dir):
                    path = os.path.join(node_dir, name)
                    if os.path.isfile(path):
                        chunk_files.append(name)
                        total_size += os.path.getsize(path)

            stats.append(
                {
                    "node_id": idx,
                    "node_name": node,
                    "chunk_count": len(chunk_files),
                    "total_size_kb": int(total_size / 1024),
                }
            )
        return stats

    def get_all_files(self) -> Dict:
        return self._read_metadata()

    def delete_file(self, file_name: str) -> bool:
        metadata = self._read_metadata()
        if file_name not in metadata:
            return False

        file_meta = metadata[file_name]
        for chunk in file_meta["chunks"]:
            for node_id in chunk["nodes"]:
                node_dir = os.path.join(self.base_dir, self.nodes[node_id])
                chunk_path = os.path.join(node_dir, chunk["chunk_id"])
                if os.path.exists(chunk_path):
                    try:
                        os.remove(chunk_path)
                    except OSError:
                        pass

        del metadata[file_name]
        self._write_metadata(metadata)
        return True
