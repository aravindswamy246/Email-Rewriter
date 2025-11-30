"""
Input folder monitoring and processing utilities for the Email Rewriter API.
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import aiofiles
from .file_handler import validate_file_type, process_input_folder_file, save_output_file


class InputFolderMonitor:
    """Monitor and process files in the input folder."""

    def __init__(self, input_dir: Path, output_dir: Path, check_interval: int = 30):
        """
        Initialize the input folder monitor.

        Args:
            input_dir: Path to input directory
            output_dir: Path to output directory
            check_interval: How often to check for new files (seconds)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.check_interval = check_interval
        self.processed_files = set()
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_for_new_files(self) -> List[Path]:
        """
        Scan input folder for new files to process.

        Returns:
            List of new file paths
        """
        if not self.input_dir.exists():
            return []

        new_files = []
        for file_path in self.input_dir.iterdir():
            if (file_path.is_file() and
                validate_file_type(file_path.name) and
                    str(file_path) not in self.processed_files):
                new_files.append(file_path)

        return sorted(new_files, key=lambda x: x.stat().st_mtime)

    async def process_file(self, file_path: Path, target_audience: str = "professional audience") -> Dict:
        """
        Process a single file from the input folder.

        Args:
            file_path: Path to the file
            target_audience: Default audience for processing

        Returns:
            Dict with processing results
        """
        try:
            self.logger.info(f"Processing file: {file_path.name}")

            # Extract text from file
            file_data = await process_input_folder_file(file_path)

            # Here you would call your email rewriting service
            # For now, we'll create a placeholder
            processed_content = f"""
Original Email:
{file_data['content']}

---
Processed for: {target_audience}
Processed at: {datetime.now().isoformat()}
File: {file_data['filename']}
            """

            # Save to output folder
            output_path = await save_output_file(
                processed_content,
                self.output_dir,
                f"processed_{file_path.stem}"
            )

            # Mark as processed
            self.processed_files.add(str(file_path))

            # Optionally move or delete the input file
            processed_dir = self.input_dir / "processed"
            processed_dir.mkdir(exist_ok=True)
            moved_path = processed_dir / file_path.name
            file_path.rename(moved_path)

            self.logger.info(
                f"Successfully processed {file_path.name} -> {output_path.name}")

            return {
                "status": "success",
                "input_file": str(file_path),
                "output_file": str(output_path),
                "moved_to": str(moved_path),
                "file_size": file_data['file_size'],
                "processing_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to process {file_path.name}: {str(e)}")

            # Move failed file to error folder
            error_dir = self.input_dir / "errors"
            error_dir.mkdir(exist_ok=True)
            error_path = error_dir / \
                f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}"
            file_path.rename(error_path)

            return {
                "status": "error",
                "input_file": str(file_path),
                "error": str(e),
                "moved_to": str(error_path),
                "processing_time": datetime.now().isoformat()
            }

    async def monitor_loop(self):
        """
        Main monitoring loop that continuously checks for new files.
        """
        self.logger.info(f"Starting input folder monitoring: {self.input_dir}")

        while True:
            try:
                new_files = self.scan_for_new_files()

                if new_files:
                    self.logger.info(
                        f"Found {len(new_files)} new files to process")

                    for file_path in new_files:
                        await self.process_file(file_path)

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)

    def start_monitoring(self):
        """
        Start the monitoring process in the background.
        """
        return asyncio.create_task(self.monitor_loop())


def get_folder_stats(folder_path: Path) -> Dict:
    """
    Get statistics about a folder.

    Args:
        folder_path: Path to folder

    Returns:
        Dict with folder statistics
    """
    if not folder_path.exists():
        return {"exists": False}

    files = list(folder_path.glob("**/*"))
    file_types = {}
    total_size = 0

    for file_path in files:
        if file_path.is_file():
            ext = file_path.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file_path.stat().st_size

    return {
        "exists": True,
        "total_files": len([f for f in files if f.is_file()]),
        "total_directories": len([f for f in files if f.is_dir()]),
        "file_types": file_types,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "supported_files": len([f for f in files if f.is_file() and validate_file_type(f.name)])
    }
