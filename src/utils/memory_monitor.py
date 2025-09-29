"""
CP2B Maps V2 - Professional Memory Monitoring and Management
Advanced memory tracking, optimization, and performance monitoring
"""

import gc
import time
import streamlit as st
from functools import wraps
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# Memory monitoring imports with error handling
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class MemoryMonitor:
    """
    Professional memory monitoring and management system
    Features: Real-time tracking, intelligent cleanup, performance alerts, session optimization
    """

    def __init__(self):
        """Initialize MemoryMonitor"""
        self.logger = get_logger(self.__class__.__name__)
        self.monitoring_enabled = HAS_PSUTIL

        if not HAS_PSUTIL:
            self.logger.warning("psutil not available - memory monitoring features disabled")

        # Memory thresholds (MB)
        self.thresholds = {
            'warning': 512,   # 512 MB
            'critical': 1024, # 1 GB
            'cleanup': 768    # 768 MB
        }

        # Session state keys that consume significant memory
        self.memory_intensive_keys = [
            'raster_data_cache',
            'shapefile_geometries',
            'municipality_data_full',
            'analysis_results_cache',
            'proximity_results',
            'map_data_cache',
            'chart_data_cache',
            'export_data_buffer'
        ]

    def get_memory_usage(self) -> float:
        """
        Get current memory usage in MB

        Returns:
            Memory usage in MB (0 if monitoring unavailable)
        """
        if not self.monitoring_enabled:
            return 0.0

        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return round(memory_mb, 2)

        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0.0

    def get_detailed_memory_info(self) -> Dict[str, Any]:
        """
        Get comprehensive memory information

        Returns:
            Dictionary with detailed memory metrics
        """
        if not self.monitoring_enabled:
            return {
                'available': False,
                'message': 'Memory monitoring requires psutil library'
            }

        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()

            return {
                'available': True,
                'process': {
                    'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                    'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                    'percent': round(process.memory_percent(), 2),
                    'pid': process.pid
                },
                'system': {
                    'total_mb': round(system_memory.total / 1024 / 1024, 2),
                    'available_mb': round(system_memory.available / 1024 / 1024, 2),
                    'used_mb': round(system_memory.used / 1024 / 1024, 2),
                    'percent': round(system_memory.percent, 2)
                },
                'thresholds': self.thresholds.copy()
            }

        except Exception as e:
            self.logger.error(f"Error getting detailed memory info: {e}")
            return {
                'available': False,
                'error': str(e)
            }

    def cleanup_memory(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Perform intelligent memory cleanup

        Args:
            aggressive: If True, performs more thorough cleanup

        Returns:
            Dictionary with cleanup results
        """
        try:
            memory_before = self.get_memory_usage()

            cleanup_results = {
                'memory_before_mb': memory_before,
                'session_keys_cleared': [],
                'cache_cleared': False,
                'gc_collected': 0,
                'aggressive': aggressive
            }

            # Clear memory-intensive session state keys
            keys_cleared = self._clear_session_state_memory()
            cleanup_results['session_keys_cleared'] = keys_cleared

            # Clear Streamlit cache if aggressive
            if aggressive:
                st.cache_data.clear()
                st.cache_resource.clear()
                cleanup_results['cache_cleared'] = True

            # Force garbage collection
            gc_count = gc.collect()
            cleanup_results['gc_collected'] = gc_count

            # Get memory after cleanup
            memory_after = self.get_memory_usage()
            cleanup_results['memory_after_mb'] = memory_after
            cleanup_results['memory_freed_mb'] = round(memory_before - memory_after, 2)

            self.logger.info(f"Memory cleanup completed: freed {cleanup_results['memory_freed_mb']} MB")

            return cleanup_results

        except Exception as e:
            self.logger.error(f"Error during memory cleanup: {e}")
            return {
                'error': str(e),
                'memory_before_mb': memory_before
            }

    def _clear_session_state_memory(self) -> List[str]:
        """Clear memory-intensive session state variables"""
        cleared_keys = []

        try:
            for key in self.memory_intensive_keys:
                if key in st.session_state:
                    # Get size estimate before deletion
                    try:
                        value = st.session_state[key]
                        if hasattr(value, '__len__'):
                            size_info = f" (size: {len(value)})"
                        else:
                            size_info = ""
                    except:
                        size_info = ""

                    del st.session_state[key]
                    cleared_keys.append(f"{key}{size_info}")

            return cleared_keys

        except Exception as e:
            self.logger.error(f"Error clearing session state: {e}")
            return cleared_keys

    def monitor_memory_threshold(self, threshold_mb: Optional[float] = None) -> Dict[str, Any]:
        """
        Monitor memory usage against threshold

        Args:
            threshold_mb: Custom threshold in MB (uses default if None)

        Returns:
            Dictionary with monitoring results and recommendations
        """
        if not self.monitoring_enabled:
            return {'monitoring_available': False}

        try:
            current_usage = self.get_memory_usage()
            threshold = threshold_mb or self.thresholds['warning']

            result = {
                'monitoring_available': True,
                'current_usage_mb': current_usage,
                'threshold_mb': threshold,
                'threshold_exceeded': current_usage > threshold,
                'usage_percentage': round((current_usage / threshold) * 100, 1) if threshold > 0 else 0
            }

            # Determine status and recommendations
            if current_usage > self.thresholds['critical']:
                result['status'] = 'critical'
                result['message'] = '🔴 Critical memory usage - immediate cleanup recommended'
                result['recommendations'] = [
                    'Clear analysis results cache',
                    'Reduce data visualization complexity',
                    'Enable aggressive memory cleanup',
                    'Consider restarting the application'
                ]
            elif current_usage > self.thresholds['cleanup']:
                result['status'] = 'high'
                result['message'] = '🟡 High memory usage - cleanup recommended'
                result['recommendations'] = [
                    'Clear unused session data',
                    'Run memory cleanup',
                    'Reduce concurrent analysis tasks'
                ]
            elif current_usage > self.thresholds['warning']:
                result['status'] = 'warning'
                result['message'] = '🟡 Elevated memory usage - monitoring recommended'
                result['recommendations'] = [
                    'Monitor memory usage',
                    'Consider clearing old results'
                ]
            else:
                result['status'] = 'normal'
                result['message'] = '🟢 Memory usage normal'
                result['recommendations'] = []

            return result

        except Exception as e:
            self.logger.error(f"Error monitoring memory threshold: {e}")
            return {
                'monitoring_available': False,
                'error': str(e)
            }

    def render_memory_widget(self, show_details: bool = False) -> None:
        """
        Render memory monitoring widget in Streamlit

        Args:
            show_details: Whether to show detailed memory information
        """
        try:
            if not self.monitoring_enabled:
                st.warning("⚠️ Memory monitoring requires psutil library")
                return

            # Get current memory info
            memory_info = self.get_detailed_memory_info()

            if not memory_info.get('available'):
                st.error(f"❌ Memory monitoring error: {memory_info.get('error', 'Unknown error')}")
                return

            process_info = memory_info['process']
            current_usage = process_info['rss_mb']

            # Memory status indicator
            threshold_result = self.monitor_memory_threshold()

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                # Main memory metric
                st.metric(
                    "Memory Usage",
                    f"{current_usage:.1f} MB",
                    delta=f"{process_info['percent']:.1f}% of system",
                    help="Current application memory usage"
                )

            with col2:
                # Status indicator
                status = threshold_result.get('status', 'normal')
                status_colors = {
                    'normal': '🟢',
                    'warning': '🟡',
                    'high': '🟠',
                    'critical': '🔴'
                }
                icon = status_colors.get(status, '⚪')
                st.markdown(f"**Status:** {icon} {status.title()}")

            with col3:
                # Cleanup button
                if st.button("🧹 Cleanup", help="Free up memory"):
                    with st.spinner("Cleaning up memory..."):
                        cleanup_result = self.cleanup_memory()

                    if 'error' not in cleanup_result:
                        freed = cleanup_result['memory_freed_mb']
                        st.success(f"✅ Freed {freed:.1f} MB")
                    else:
                        st.error("❌ Cleanup failed")

            # Show warning/recommendations if needed
            if threshold_result.get('threshold_exceeded'):
                st.warning(threshold_result['message'])

                if threshold_result.get('recommendations'):
                    with st.expander("💡 Recommendations"):
                        for rec in threshold_result['recommendations']:
                            st.markdown(f"• {rec}")

            # Detailed information
            if show_details:
                with st.expander("📊 Detailed Memory Information"):
                    system_info = memory_info['system']

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Process Memory:**")
                        st.write(f"RSS: {process_info['rss_mb']:.1f} MB")
                        st.write(f"VMS: {process_info['vms_mb']:.1f} MB")
                        st.write(f"Process %: {process_info['percent']:.2f}%")

                    with col2:
                        st.markdown("**System Memory:**")
                        st.write(f"Total: {system_info['total_mb']:,.0f} MB")
                        st.write(f"Available: {system_info['available_mb']:,.0f} MB")
                        st.write(f"System %: {system_info['percent']:.1f}%")

        except Exception as e:
            self.logger.error(f"Error rendering memory widget: {e}")
            st.error("⚠️ Error displaying memory information")

    def get_session_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of session state memory usage

        Returns:
            Dictionary with session state analysis
        """
        try:
            summary = {
                'total_keys': len(st.session_state),
                'memory_intensive_keys_present': [],
                'large_objects': [],
                'estimated_memory_usage': 'N/A'
            }

            # Check for memory-intensive keys
            for key in self.memory_intensive_keys:
                if key in st.session_state:
                    summary['memory_intensive_keys_present'].append(key)

            # Find large objects in session state
            for key, value in st.session_state.items():
                try:
                    if hasattr(value, '__len__') and len(value) > 1000:
                        summary['large_objects'].append({
                            'key': key,
                            'size': len(value),
                            'type': type(value).__name__
                        })
                except:
                    pass  # Skip objects that don't support len()

            return summary

        except Exception as e:
            self.logger.error(f"Error analyzing session state: {e}")
            return {'error': str(e)}


# Memory monitoring decorator
def monitor_memory(threshold_mb: float = 512):
    """
    Decorator to monitor memory usage of functions

    Args:
        threshold_mb: Memory threshold in MB for warnings

    Returns:
        Decorated function with memory monitoring
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_memory_monitor()

            if not monitor.monitoring_enabled:
                return func(*args, **kwargs)

            # Memory before execution
            memory_before = monitor.get_memory_usage()

            try:
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Memory after execution
                memory_after = monitor.get_memory_usage()
                memory_delta = memory_after - memory_before

                # Log performance metrics
                logger.info(
                    f"Function {func.__name__} - "
                    f"Memory: {memory_delta:+.1f}MB "
                    f"(before: {memory_before:.1f}MB, after: {memory_after:.1f}MB), "
                    f"Time: {execution_time:.2f}s"
                )

                # Check threshold
                if memory_after > threshold_mb:
                    logger.warning(
                        f"Memory threshold exceeded in {func.__name__}: "
                        f"{memory_after:.1f}MB > {threshold_mb}MB"
                    )

                return result

            except Exception as e:
                memory_after = monitor.get_memory_usage()
                logger.error(
                    f"Error in {func.__name__} - Memory: {memory_after:.1f}MB - Error: {e}"
                )
                raise

        return wrapper
    return decorator


# Performance tracking decorator
def track_performance(log_level: str = 'INFO'):
    """
    Decorator to track function performance

    Args:
        log_level: Logging level for performance metrics

    Returns:
        Decorated function with performance tracking
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = get_memory_monitor().get_memory_usage()

            try:
                result = func(*args, **kwargs)

                end_time = time.time()
                end_memory = get_memory_monitor().get_memory_usage()

                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory

                # Log performance
                log_func = getattr(logger, log_level.lower(), logger.info)
                log_func(
                    f"Performance - {func.__name__}: "
                    f"{execution_time:.3f}s, {memory_delta:+.1f}MB"
                )

                return result

            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"Performance - {func.__name__} failed after {execution_time:.3f}s: {e}")
                raise

        return wrapper
    return decorator


# Factory function
@st.cache_resource
def get_memory_monitor() -> MemoryMonitor:
    """
    Get cached MemoryMonitor instance

    Returns:
        MemoryMonitor instance
    """
    return MemoryMonitor()


# Convenience functions
def cleanup_memory(aggressive: bool = False) -> Dict[str, Any]:
    """
    Convenience function for memory cleanup

    Args:
        aggressive: Whether to perform aggressive cleanup

    Returns:
        Cleanup results dictionary
    """
    monitor = get_memory_monitor()
    return monitor.cleanup_memory(aggressive)


def get_memory_usage() -> float:
    """
    Convenience function to get current memory usage

    Returns:
        Memory usage in MB
    """
    monitor = get_memory_monitor()
    return monitor.get_memory_usage()


def render_memory_monitor(show_details: bool = False) -> None:
    """
    Convenience function to render memory monitoring widget

    Args:
        show_details: Whether to show detailed information
    """
    monitor = get_memory_monitor()
    monitor.render_memory_widget(show_details)