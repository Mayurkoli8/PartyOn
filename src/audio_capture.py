"""
Audio capture module for the Audio Streamer server.

Handles device discovery and audio capture via WASAPI loopback or Stereo Mix.
"""

import logging
from typing import Optional, List, Tuple

import sounddevice as sd
import numpy as np

from .config import ServerConfig


class AudioCapture:
    """Encapsulates audio device discovery and capture logic."""
    
    def __init__(self, config: ServerConfig, logger: logging.Logger):
        """
        Initialize the audio capture module.
        
        Args:
            config: Server configuration.
            logger: Logger instance for this module.
        """
        self.config = config
        self.logger = logger
        self.stream: Optional[sd.InputStream] = None
        self.is_running: bool = False
        self.device_name: str = "Unknown"
    
    def initialize(self) -> bool:
        """
        Discover and initialize audio capture device.
        
        Returns:
            True if initialization succeeded, False otherwise.
        """
        devices = self._list_devices()
        
        # Try WASAPI loopback first
        out_candidates = [
            i for i, d in enumerate(devices) 
            if d['max_output_channels'] > 0
        ]
        
        for idx in out_candidates:
            if self._try_wasapi(idx):
                self.is_running = True
                return True
        
        # Fall back to Stereo Mix
        self.logger.info("WASAPI loopback failed, trying Stereo Mix fallback")
        stereo_candidates = [
            i for i, d in enumerate(devices)
            if "stereo" in d['name'].lower() or d['max_input_channels'] > 0
        ]
        
        if self._try_stereo_mix(stereo_candidates):
            self.is_running = True
            return True
        
        self.logger.error(
            "No audio source found. Enable Stereo Mix or WASAPI loopback "
            "in Windows sound settings."
        )
        return False
    
    def read_block(self) -> Optional[bytes]:
        """
        Read a block of audio data.
        
        Returns:
            Raw audio bytes, or None on error.
        """
        if not self.stream or not self.is_running:
            return None
        
        try:
            frames, _ = self.stream.read(self.config.block_size)
            return frames.tobytes()
        except Exception as e:
            self.logger.error(f"Error reading audio block: {e}")
            return None
    
    def stop(self) -> None:
        """Stop capture and release device."""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                self.logger.warning(f"Error stopping audio stream: {e}")
            finally:
                self.stream = None
                self.is_running = False
        self.logger.info("Audio capture stopped")
    
    def reinitialize(self) -> bool:
        """
        Attempt to reinitialize after device error.
        
        Returns:
            True if reinitialization succeeded, False otherwise.
        """
        self.logger.info("Attempting to reinitialize audio capture")
        self.stop()
        return self.initialize()
    
    def _list_devices(self) -> List[dict]:
        """List available audio devices."""
        devices = sd.query_devices()
        self.logger.debug("Available audio devices:")
        for i, d in enumerate(devices):
            self.logger.debug(
                f"  {i}: {d['name']} | out: {d['max_output_channels']} "
                f"in: {d['max_input_channels']}"
            )
        return devices
    
    def _try_wasapi(self, idx: int) -> bool:
        """Try to open WASAPI loopback on the given device index."""
        try:
            self.logger.debug(f"Trying WASAPI loopback on device {idx}")
            
            try:
                ws = sd.WasapiSettings(loopback=True)
            except AttributeError:
                ws = None
            
            self.stream = sd.InputStream(
                device=idx,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                blocksize=self.config.block_size,
                dtype="int16",
                extra_settings=ws
            )
            self.stream.start()
            
            device_info = sd.query_devices(idx)
            self.device_name = device_info['name']
            self.logger.info(f"WASAPI loopback success on device {idx}: {self.device_name}")
            return True
            
        except Exception as e:
            self.logger.debug(f"WASAPI failed on device {idx}: {e}")
            return False
    
    def _try_stereo_mix(self, candidates: List[int]) -> bool:
        """Try to open Stereo Mix on candidate devices."""
        for idx in candidates:
            try:
                self.logger.debug(f"Trying Stereo Mix on device {idx}")
                
                self.stream = sd.InputStream(
                    device=idx,
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    blocksize=self.config.block_size,
                    dtype="int16"
                )
                self.stream.start()
                
                device_info = sd.query_devices(idx)
                self.device_name = device_info['name']
                self.logger.info(f"Stereo Mix success on device {idx}: {self.device_name}")
                return True
                
            except Exception as e:
                self.logger.debug(f"Stereo Mix failed on device {idx}: {e}")
        
        return False
    
    def get_device_info(self) -> dict:
        """Get information about the current audio device."""
        return {
            "device": self.device_name,
            "sample_rate": self.config.sample_rate,
            "channels": self.config.channels,
            "is_running": self.is_running
        }
