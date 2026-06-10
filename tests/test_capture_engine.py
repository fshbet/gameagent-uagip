"""
Unit tests for UAGIP Capture Engine.
"""

import unittest
from unittest.mock import Mock, patch
import numpy as np
import time

from capture.frame import Frame
from capture.capture_source import CaptureSource
from capture.screen_capture import ScreenCapture
from capture.frame_buffer import FrameBuffer
from capture.capture_manager import CaptureManager
from capture.capture_metrics import CaptureMetrics


class TestFrame(unittest.TestCase):
    """Test Frame class functionality."""
    
    def test_frame_creation(self):
        """Test creating a frame with all fields."""
        # Create a mock image array
        image = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        
        frame = Frame(
            frame_id="test_001",
            timestamp=1234567890.0,
            width=640,
            height=480,
            source="test_source",
            image=image,
            metadata={"test": "data"}
        )
        
        self.assertEqual(frame.frame_id, "test_001")
        self.assertEqual(frame.timestamp, 1234567890.0)
        self.assertEqual(frame.width, 640)
        self.assertEqual(frame.height, 480)
        self.assertEqual(frame.source, "test_source")
        self.assertTrue(np.array_equal(frame.image, image))
        self.assertEqual(frame.metadata, {"test": "data"})
        
    def test_frame_serialization(self):
        """Test frame serialization functionality."""
        # Create a mock image array
        image = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        
        frame = Frame(
            frame_id="test_001",
            timestamp=1234567890.0,
            width=640,
            height=480,
            source="test_source",
            image=image,
            metadata={"test": "data"}
        )
        
        # Test that serialization works (should not raise exceptions)
        serialized = frame.__dict__
        self.assertIn('frame_id', serialized)
        self.assertIn('timestamp', serialized)
        self.assertIn('width', serialized)
        self.assertIn('height', serialized)
        self.assertIn('source', serialized)
        self.assertIn('image', serialized)
        self.assertIn('metadata', serialized)


class TestFrameBuffer(unittest.TestCase):
    """Test FrameBuffer class functionality."""
    
    def test_buffer_creation(self):
        """Test creating a frame buffer."""
        buffer = FrameBuffer(capacity=10)
        self.assertEqual(buffer.capacity(), 10)
        self.assertEqual(buffer.size(), 0)
        self.assertFalse(buffer.is_full())
        
    def test_add_frame(self):
        """Test adding frames to buffer."""
        buffer = FrameBuffer(capacity=3)
        
        # Create mock frames
        frame1 = Mock(spec=Frame)
        frame1.frame_id = "frame1"
        frame2 = Mock(spec=Frame)
        frame2.frame_id = "frame2"
        frame3 = Mock(spec=Frame)
        frame3.frame_id = "frame3"
        
        # Add frames
        buffer.add_frame(frame1)
        buffer.add_frame(frame2)
        buffer.add_frame(frame3)
        
        self.assertEqual(buffer.size(), 3)
        self.assertTrue(buffer.is_full())
        
        # Test adding more frames (should overwrite oldest)
        frame4 = Mock(spec=Frame)
        frame4.frame_id = "frame4"
        buffer.add_frame(frame4)
        
        self.assertEqual(buffer.size(), 3)
        self.assertTrue(buffer.is_full())
        
    def test_get_latest(self):
        """Test getting the latest frame."""
        buffer = FrameBuffer(capacity=3)
        
        # Create mock frames
        frame1 = Mock(spec=Frame)
        frame1.frame_id = "frame1"
        frame2 = Mock(spec=Frame)
        frame2.frame_id = "frame2"
        
        # Add frames
        buffer.add_frame(frame1)
        buffer.add_frame(frame2)
        
        latest = buffer.get_latest()
        self.assertEqual(latest.frame_id, "frame2")
        
    def test_get_last_n(self):
        """Test getting last N frames."""
        buffer = FrameBuffer(capacity=5)
        
        # Create mock frames
        frames = [Mock(spec=Frame) for _ in range(5)]
        for i, frame in enumerate(frames):
            frame.frame_id = f"frame{i+1}"
            
        # Add frames
        for frame in frames:
            buffer.add_frame(frame)
            
        last_3 = buffer.get_last_n(3)
        self.assertEqual(len(last_3), 3)
        self.assertEqual(last_3[0].frame_id, "frame5")  # Most recent first
        self.assertEqual(last_3[1].frame_id, "frame4")
        self.assertEqual(last_3[2].frame_id, "frame3")
        
    def test_clear(self):
        """Test clearing the buffer."""
        buffer = FrameBuffer(capacity=3)
        
        # Add some frames
        frame1 = Mock(spec=Frame)
        frame1.frame_id = "frame1"
        buffer.add_frame(frame1)
        
        self.assertEqual(buffer.size(), 1)
        buffer.clear()
        self.assertEqual(buffer.size(), 0)
        
    def test_buffer_thread_safety(self):
        """Test that buffer operations are thread-safe."""
        buffer = FrameBuffer(capacity=10)
        
        # Create multiple threads to add frames
        import threading
        
        def add_frames():
            for i in range(5):
                frame = Mock(spec=Frame)
                frame.frame_id = f"thread_frame_{i}"
                buffer.add_frame(frame)
                
        threads = [threading.Thread(target=add_frames) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        # Should have added 15 frames total
        self.assertEqual(buffer.size(), 10)  # Buffer capacity is 10


class TestCaptureMetrics(unittest.TestCase):
    """Test CaptureMetrics class functionality."""
    
    def test_metrics_initialization(self):
        """Test creating capture metrics."""
        metrics = CaptureMetrics()
        self.assertIsNone(metrics.start_time)
        self.assertIsNone(metrics.stop_time)
        self.assertEqual(metrics.frame_count, 0)
        self.assertEqual(metrics.dropped_frames, 0)
        self.assertEqual(metrics.fps, 0.0)
        self.assertEqual(metrics.average_latency, 0.0)
        
    def test_update_fps(self):
        """Test updating FPS metrics."""
        metrics = CaptureMetrics()
        metrics.update_fps(10)
        metrics.update_fps(5)
        
        # Should have updated frame count
        self.assertEqual(metrics.frame_count, 15)
        
    def test_update_latency(self):
        """Test updating latency metrics."""
        metrics = CaptureMetrics()
        metrics.update_latency(0.01)
        metrics.update_latency(0.02)
        
        # Should have updated latency samples
        self.assertEqual(len(metrics._latency_samples), 2)
        self.assertEqual(metrics.average_latency, 0.015)
        
    def test_update_dropped_frames(self):
        """Test updating dropped frames."""
        metrics = CaptureMetrics()
        metrics.update_dropped_frames(3)
        metrics.update_dropped_frames(2)
        
        self.assertEqual(metrics.dropped_frames, 5)
        
    def test_capture_uptime(self):
        """Test capture uptime calculation."""
        metrics = CaptureMetrics()
        metrics.start_time = time.time() - 10  # 10 seconds ago
        
        uptime = metrics.capture_uptime
        self.assertGreaterEqual(uptime, 9.0)  # Should be at least 9 seconds
        self.assertLessEqual(uptime, 11.0)  # Should be at most 11 seconds
        
    def test_is_active(self):
        """Test active status."""
        metrics = CaptureMetrics()
        self.assertFalse(metrics.is_active)
        
        metrics.start_time = time.time()
        self.assertTrue(metrics.is_active)
        
        metrics.stop_time = time.time()
        self.assertFalse(metrics.is_active)
        
    def test_get_metrics(self):
        """Test getting all metrics as dict."""
        metrics = CaptureMetrics()
        metrics.update_fps(10)
        metrics.update_latency(0.01)
        metrics.update_dropped_frames(2)
        
        result = metrics.get_metrics()
        self.assertIn('fps', result)
        self.assertIn('average_latency', result)
        self.assertIn('dropped_frames', result)
        self.assertIn('frame_count', result)
        self.assertIn('capture_uptime', result)
        self.assertIn('is_active', result)


class TestCaptureManager(unittest.TestCase):
    """Test CaptureManager class functionality."""
    
    def test_manager_creation(self):
        """Test creating capture manager."""
        manager = CaptureManager()
        self.assertEqual(len(manager.list_sources()), 0)
        
    def test_register_source(self):
        """Test registering a capture source."""
        manager = CaptureManager()
        
        # Create mock source
        source = Mock(spec=CaptureSource)
        source.name = "test_source"
        
        success = manager.register_source(source)
        self.assertTrue(success)
        self.assertIn("test_source", manager.list_sources())
        
        # Try to register again (should fail)
        success = manager.register_source(source)
        self.assertFalse(success)
        
    def test_remove_source(self):
        """Test removing a capture source."""
        manager = CaptureManager()
        
        # Create mock source
        source = Mock(spec=CaptureSource)
        source.name = "test_source"
        source.is_running.return_value = False
        
        manager.register_source(source)
        self.assertIn("test_source", manager.list_sources())
        
        success = manager.remove_source("test_source")
        self.assertTrue(success)
        self.assertNotIn("test_source", manager.list_sources())
        
    def test_start_stop_source(self):
        """Test starting and stopping a source."""
        manager = CaptureManager()
        
        # Create mock source
        source = Mock(spec=CaptureSource)
        source.name = "test_source"
        source.start.return_value = True
        source.stop.return_value = True
        source.is_running.return_value = False
        
        manager.register_source(source)
        
        success = manager.start_source("test_source")
        self.assertTrue(success)
        
        success = manager.stop_source("test_source")
        self.assertTrue(success)
        
    def test_get_frame(self):
        """Test getting a frame from source."""
        manager = CaptureManager()
        
        # Create mock source and frame
        frame = Mock(spec=Frame)
        frame.frame_id = "test_frame"
        frame.timestamp = 1234567890.0
        
        source = Mock(spec=CaptureSource)
        source.name = "test_source"
        source.get_frame.return_value = frame
        
        manager.register_source(source)
        manager.start_source("test_source")
        
        result_frame = manager.get_frame("test_source")
        self.assertEqual(result_frame.frame_id, "test_frame")


class TestScreenCapture(unittest.TestCase):
    """Test ScreenCapture class functionality."""
    
    def test_screen_capture_creation(self):
        """Test creating screen capture."""
        # This test will only verify the class can be instantiated
        # Actual capture behavior will be tested with mocks

        # Create a mock for mss
        with patch('mss.mss') as mock_mss:
            # Mock the mss context manager
            mock_instance = Mock()
            mock_mss.return_value.__enter__.return_value = mock_instance

            capture = ScreenCapture("test_source")
            self.assertIsNotNone(capture)
            
    def test_screen_capture_methods(self):
        """Test screen capture methods exist."""
        with patch('mss.mss') as mock_mss:
            # Mock the mss context manager
            mock_instance = Mock()
            mock_mss.return_value.__enter__.return_value = mock_instance
            
            capture = ScreenCapture("test_source")
            
            # Test that required methods exist
            self.assertTrue(hasattr(capture, 'start'))
            self.assertTrue(hasattr(capture, 'stop'))
            self.assertTrue(hasattr(capture, 'get_frame'))
            self.assertTrue(hasattr(capture, 'is_running'))


if __name__ == '__main__':
    unittest.main()