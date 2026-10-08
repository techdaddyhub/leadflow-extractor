"""
LeadFlow Intelligence Suite - QThread Async Crawl Worker
Runs asynchronous extraction in a detached background thread to guarantee smooth 60fps UI.
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from ..core.crawler import AsyncCrawler
from ..core.extractor import ExtractedLead
from ..utils.config import CrawlConfig


class CrawlWorker(QThread):
    """Worker thread bridging async crawler events with PyQt signals."""

    lead_found = pyqtSignal(dict)
    progress_updated = pyqtSignal(dict)
    log_message = pyqtSignal(str, str)
    status_changed = pyqtSignal(str)
    finished_crawl = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, config: CrawlConfig, parent: Optional[Any] = None):
        super().__init__(parent)
        self.config = config
        self._crawler: Optional[AsyncCrawler] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_paused = False

    def pause(self) -> None:
        """Pauses the async crawler."""
        if self._crawler and not self.is_paused:
            self.is_paused = True
            self._crawler.pause()
            self.status_changed.emit("Paused")

    def resume(self) -> None:
        """Resumes the async crawler."""
        if self._crawler and self.is_paused:
            self.is_paused = False
            self._crawler.resume()
            self.status_changed.emit("Running")

    def stop(self) -> None:
        """Instructs the crawler to stop and abort loop."""
        if self._crawler:
            self._crawler.stop()
            self.status_changed.emit("Stopping...")

    def _on_lead(self, lead: ExtractedLead) -> None:
        self.lead_found.emit(lead.to_dict())

    def _on_progress(self, stats: Dict[str, Any]) -> None:
        self.progress_updated.emit(stats)

    def _on_log(self, level: str, message: str) -> None:
        self.log_message.emit(level, message)

    def run(self) -> None:
        """Executes the asynchronous event loop inside the worker thread."""
        self.status_changed.emit("Running")
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._crawler = AsyncCrawler(
            config=self.config,
            on_lead_found=self._on_lead,
            on_progress=self._on_progress,
            on_log=self._on_log,
        )

        try:
            self._loop.run_until_complete(self._crawler.run())
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit("ERROR", f"Worker runtime exception: {e}")
        finally:
            try:
                # Cancel pending tasks
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                self._loop.close()
            except Exception:
                pass

            self.status_changed.emit("Idle")
            self.finished_crawl.emit()

