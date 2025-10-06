"""
Loading States Component for CP2B Maps
Professional loading animations and progress indicators (V1 style)
SOLID: Single Responsibility - Display loading states and progress
"""

import streamlit as st
import time
from typing import Optional, Callable, Any
from contextlib import contextmanager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@contextmanager
def loading_spinner(message: str = "Carregando...", spinner_type: str = "default"):
    """
    Context manager for loading spinner with V1-style messaging

    Args:
        message: Loading message to display
        spinner_type: Type of spinner (default, dots, growing, etc.)

    Usage:
        with loading_spinner("Carregando dados..."):
            # Your code here
            data = load_data()
    """
    try:
        with st.spinner(message):
            yield
    except Exception as e:
        logger.error(f"Error during loading: {e}")
        raise


def show_progress_bar(current: int, total: int, message: str = "") -> None:
    """
    Display progress bar with percentage

    Args:
        current: Current progress value
        total: Total progress value
        message: Optional message to display above progress
    """
    try:
        if total > 0:
            progress = current / total

            if message:
                st.caption(message)

            st.progress(progress, text=f"{int(progress * 100)}% completo")

    except Exception as e:
        logger.error(f"Error displaying progress bar: {e}")


def show_loading_message(
    message: str,
    icon: str = "⏳",
    message_type: str = "info"
) -> None:
    """
    Show loading message with icon (V1 style)

    Args:
        message: Message to display
        icon: Icon emoji
        message_type: Type (info, warning, success)
    """
    full_message = f"{icon} {message}"

    if message_type == "info":
        st.info(full_message)
    elif message_type == "warning":
        st.warning(full_message)
    elif message_type == "success":
        st.success(full_message)
    else:
        st.write(full_message)


def render_skeleton_loader(num_items: int = 3) -> None:
    """
    Render skeleton placeholder for loading content

    Args:
        num_items: Number of skeleton items to show
    """
    st.markdown("""
    <style>
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: 4px;
        height: 60px;
        margin-bottom: 10px;
    }

    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    for i in range(num_items):
        st.markdown(f'<div class="skeleton"></div>', unsafe_allow_html=True)


def execute_with_loading(
    func: Callable,
    *args,
    loading_message: str = "Processando...",
    success_message: Optional[str] = None,
    error_message: str = "Erro ao processar",
    **kwargs
) -> Any:
    """
    Execute function with loading indicator

    Args:
        func: Function to execute
        loading_message: Message during loading
        success_message: Message on success (optional)
        error_message: Message on error
        *args, **kwargs: Arguments for func

    Returns:
        Result of func execution
    """
    try:
        with st.spinner(loading_message):
            result = func(*args, **kwargs)

        if success_message:
            st.success(success_message)

        return result

    except Exception as e:
        logger.error(f"Error executing function: {e}", exc_info=True)
        st.error(f"{error_message}: {str(e)}")
        return None


def show_data_loading_stages(stages: list[str], current_stage: int = 0) -> None:
    """
    Show multi-stage loading progress (V1 style)

    Args:
        stages: List of stage names
        current_stage: Current stage index (0-based)
    """
    st.markdown("### 🔄 Carregando Dados")

    for idx, stage in enumerate(stages):
        if idx < current_stage:
            st.success(f"✅ {stage}")
        elif idx == current_stage:
            st.info(f"⏳ {stage}...")
        else:
            st.caption(f"⏸️ {stage}")


class LoadingState:
    """
    Class to manage loading states across components
    Useful for complex multi-step operations
    """

    def __init__(self, total_steps: int, description: str = "Processando"):
        """
        Initialize loading state manager

        Args:
            total_steps: Total number of steps
            description: Overall process description
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.step_descriptions = []
        self.container = st.empty()

    def update(self, step_description: str) -> None:
        """Update to next step with description"""
        self.current_step += 1
        self.step_descriptions.append(step_description)

        with self.container:
            progress = self.current_step / self.total_steps
            st.progress(progress)
            st.caption(f"**{self.description}**: {step_description} ({self.current_step}/{self.total_steps})")

    def complete(self, message: str = "Concluído!") -> None:
        """Mark loading as complete"""
        with self.container:
            st.success(f"✅ {message}")

    def error(self, message: str) -> None:
        """Mark loading as failed"""
        with self.container:
            st.error(f"❌ {message}")


def render_minimal_loader(message: str = "Carregando...") -> None:
    """
    Minimal loader for quick operations
    Just shows a small message, no blocking UI
    """
    st.markdown(
        f'<p style="color: #666; font-size: 14px; font-style: italic;">⏳ {message}</p>',
        unsafe_allow_html=True
    )
