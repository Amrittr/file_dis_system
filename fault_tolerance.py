import threading
import time
from typing import Callable, Dict, List, Optional


class FaultToleranceMonitor:
    def __init__(
        self,
        num_nodes: int = 3,
        heartbeat_interval: int = 3,
        on_failure_callback: Optional[Callable[[int], None]] = None,
    ):
        self.num_nodes = num_nodes
        self.heartbeat_interval = heartbeat_interval
        self.on_failure_callback = on_failure_callback
        self.node_states: Dict[int, bool] = {i: True for i in range(self.num_nodes)}
        self.event_log: List[str] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()
        self.log_event("Heartbeat monitor started")

    def stop(self) -> None:
        self._running = False
        self.log_event("Heartbeat monitor stopped")

    def _heartbeat_loop(self) -> None:
        while self._running:
            time.sleep(self.heartbeat_interval)

    def simulate_failure(self, node_id: int) -> None:
        if not self.node_states.get(node_id, False):
            return
        self.node_states[node_id] = False
        self.log_event(f"Node {node_id + 1} failed")
        if self.on_failure_callback:
            self.on_failure_callback(node_id)

    def restore_node(self, node_id: int) -> None:
        if self.node_states.get(node_id, True):
            return
        self.node_states[node_id] = True
        self.log_event(f"Node {node_id + 1} restored")

    def get_failed_nodes(self) -> List[int]:
        return [i for i, alive in self.node_states.items() if not alive]

    def get_healthy_nodes(self) -> List[int]:
        return [i for i, alive in self.node_states.items() if alive]

    def is_alive(self, node_id: int) -> bool:
        return self.node_states.get(node_id, False)

    def log_event(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
        if len(self.event_log) > 200:
            self.event_log = self.event_log[-200:]

    def get_log(self) -> List[str]:
        return list(self.event_log)
