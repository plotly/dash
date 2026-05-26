"""WebSocket callback registry for handling reconnections.

This module provides a registry that tracks active callbacks per renderer,
allowing callbacks to persist across WebSocket reconnections.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    import queue
    import janus


@dataclass
class RendererState:
    """State for a single renderer's WebSocket connection."""

    outbound_queue: "janus.Queue[str]"
    pending_get_props: Dict[str, "queue.Queue[Any]"]
    shutdown_event: threading.Event
    active_callback_count: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class ActiveCallbackRegistry:
    """Registry for active WebSocket callbacks that persists across reconnections.

    When a WebSocket disconnects and reconnects, callbacks that are still running
    can "adopt" the new connection's queues to continue sending updates.

    Thread-safe for access from both the main event loop and worker threads.
    """

    def __init__(self) -> None:
        self._renderers: Dict[str, RendererState] = {}
        self._lock = threading.Lock()

    def adopt_connection(
        self,
        renderer_id: str,
        outbound_queue: "janus.Queue[str]",
        pending_get_props: Dict[str, "queue.Queue[Any]"],
        shutdown_event: threading.Event,
    ) -> None:
        """Associate new connection with existing callbacks for this renderer.

        When a WebSocket reconnects, this method updates the queues and shutdown
        event so that running callbacks can use the new connection.

        Args:
            renderer_id: The renderer ID for this connection
            outbound_queue: janus.Queue for sending messages
            pending_get_props: Dict to track pending get_props requests
            shutdown_event: Event signaling connection closure
        """
        with self._lock:
            if renderer_id in self._renderers:
                state = self._renderers[renderer_id]
                with state.lock:
                    state.outbound_queue = outbound_queue
                    state.pending_get_props = pending_get_props
                    state.shutdown_event = shutdown_event
            else:
                self._renderers[renderer_id] = RendererState(
                    outbound_queue=outbound_queue,
                    pending_get_props=pending_get_props,
                    shutdown_event=shutdown_event,
                    active_callback_count=0,
                )

    def register_callback(self, renderer_id: str) -> None:
        """Register a new active callback for this renderer.

        Args:
            renderer_id: The renderer ID
        """
        with self._lock:
            if renderer_id in self._renderers:
                state = self._renderers[renderer_id]
                with state.lock:
                    state.active_callback_count += 1

    def unregister_callback(self, renderer_id: str) -> None:
        """Unregister a completed callback for this renderer.

        If no active callbacks remain, the renderer state is cleaned up.

        Args:
            renderer_id: The renderer ID
        """
        with self._lock:
            if renderer_id in self._renderers:
                state = self._renderers[renderer_id]
                with state.lock:
                    state.active_callback_count -= 1
                    if state.active_callback_count <= 0:
                        del self._renderers[renderer_id]

    def get_queue(self, renderer_id: str) -> Optional["janus.Queue[str]"]:
        """Get current outbound queue for renderer (thread-safe).

        Args:
            renderer_id: The renderer ID

        Returns:
            The current outbound queue, or None if renderer not found
        """
        with self._lock:
            state = self._renderers.get(renderer_id)
            if state is None:
                return None
            with state.lock:
                return state.outbound_queue

    def get_pending_get_props(
        self, renderer_id: str
    ) -> Optional[Dict[str, "queue.Queue[Any]"]]:
        """Get current pending_get_props dict for renderer (thread-safe).

        Args:
            renderer_id: The renderer ID

        Returns:
            The current pending_get_props dict, or None if renderer not found
        """
        with self._lock:
            state = self._renderers.get(renderer_id)
            if state is None:
                return None
            with state.lock:
                return state.pending_get_props

    def is_shutdown(self, renderer_id: str) -> bool:
        """Check if current connection is shutdown.

        Args:
            renderer_id: The renderer ID

        Returns:
            True if shutdown event is set or renderer not found, False otherwise
        """
        with self._lock:
            state = self._renderers.get(renderer_id)
            if state is None:
                return True
            with state.lock:
                return state.shutdown_event.is_set()

    def cleanup_renderer(self, renderer_id: str) -> None:
        """Clean up renderer state when connection closes.

        Only removes if no active callbacks remain.

        Args:
            renderer_id: The renderer ID to clean up
        """
        with self._lock:
            state = self._renderers.get(renderer_id)
            if state is not None:
                with state.lock:
                    if state.active_callback_count <= 0:
                        del self._renderers[renderer_id]
