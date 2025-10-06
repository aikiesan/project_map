"""
CP2B Maps - Accessible Components
WCAG 2.1 Level A compliant Streamlit components
"""

import streamlit as st
from typing import Optional, List, Any, Dict
import uuid

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def accessible_button(
    label: str,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    aria_label: Optional[str] = None,
    disabled: bool = False
) -> bool:
    """
    Create WCAG 2.1 Level A compliant button

    Args:
        label: Button text
        key: Unique key for the button
        help_text: Help text for accessibility
        aria_label: ARIA label (defaults to label)
        disabled: Whether button is disabled

    Returns:
        Boolean indicating if button was clicked
    """
    try:
        # Use provided aria_label or default to label
        aria_label = aria_label or label

        # Create button with accessibility attributes
        button_clicked = st.button(
            label,
            key=key,
            help=help_text,
            disabled=disabled,
            use_container_width=False
        )

        # Add ARIA label via JavaScript if different from label
        if aria_label != label and key:
            aria_script = f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const button = document.querySelector('[data-testid="baseButton-secondary"]:has-text("{label}")');
                if (button) {{
                    button.setAttribute('aria-label', '{aria_label}');
                    button.setAttribute('role', 'button');
                }}
            }});
            </script>
            """
            st.markdown(aria_script, unsafe_allow_html=True)

        return button_clicked

    except Exception as e:
        logger.error(f"Error creating accessible button: {e}")
        return st.button(label, key=key, disabled=disabled)


def accessible_selectbox(
    label: str,
    options: List[Any],
    index: int = 0,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    aria_label: Optional[str] = None
) -> Any:
    """
    Create WCAG 2.1 Level A compliant selectbox

    Args:
        label: Label for the selectbox
        options: List of options
        index: Default selected index
        key: Unique key for the selectbox
        help_text: Help text for accessibility
        aria_label: ARIA label (defaults to label)

    Returns:
        Selected option
    """
    try:
        # Ensure proper labeling (WCAG 3.3.2)
        if help_text:
            st.markdown(f"**{label}**")
            st.markdown(f"*{help_text}*")

        # Create selectbox with accessibility features
        selected = st.selectbox(
            label,
            options=options,
            index=index,
            key=key,
            help=help_text
        )

        # Add ARIA attributes via JavaScript
        if key:
            aria_label_attr = aria_label or label
            aria_script = f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const selectbox = document.querySelector('[data-baseweb="select"]');
                if (selectbox) {{
                    selectbox.setAttribute('aria-label', '{aria_label_attr}');
                    selectbox.setAttribute('role', 'combobox');
                    selectbox.setAttribute('aria-expanded', 'false');
                }}
            }});
            </script>
            """
            st.markdown(aria_script, unsafe_allow_html=True)

        return selected

    except Exception as e:
        logger.error(f"Error creating accessible selectbox: {e}")
        return st.selectbox(label, options, index=index, key=key)


def accessible_text_input(
    label: str,
    value: str = "",
    max_chars: Optional[int] = None,
    key: Optional[str] = None,
    type_: str = "default",
    help_text: Optional[str] = None,
    placeholder: Optional[str] = None,
    aria_label: Optional[str] = None,
    required: bool = False
) -> str:
    """
    Create WCAG 2.1 Level A compliant text input

    Args:
        label: Label for the input
        value: Default value
        max_chars: Maximum character limit
        key: Unique key for the input
        type_: Input type ('default' or 'password')
        help_text: Help text for accessibility
        placeholder: Placeholder text
        aria_label: ARIA label (defaults to label)
        required: Whether field is required

    Returns:
        Input value
    """
    try:
        # Enhanced label with required indicator (WCAG 3.3.2)
        enhanced_label = f"{label}{'*' if required else ''}"

        if help_text:
            st.markdown(f"**{enhanced_label}**")
            st.markdown(f"*{help_text}*")

        # Create text input
        input_value = st.text_input(
            enhanced_label,
            value=value,
            max_chars=max_chars,
            key=key,
            type=type_,
            help=help_text,
            placeholder=placeholder
        )

        # Add accessibility attributes via JavaScript
        if key:
            aria_label_attr = aria_label or label
            required_attr = "true" if required else "false"

            aria_script = f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const input = document.querySelector('input[type="text"], input[type="password"]');
                if (input) {{
                    input.setAttribute('aria-label', '{aria_label_attr}');
                    input.setAttribute('aria-required', '{required_attr}');
                    if ('{placeholder}') {{
                        input.setAttribute('aria-describedby', 'placeholder-{key}');
                    }}
                }}
            }});
            </script>
            """
            st.markdown(aria_script, unsafe_allow_html=True)

        # Validation for required fields (WCAG 3.3.1)
        if required and not input_value.strip():
            st.markdown(
                '<div class="accessibility-error" role="alert" aria-live="polite">'
                f'⚠️ {label} é obrigatório</div>',
                unsafe_allow_html=True
            )

        return input_value

    except Exception as e:
        logger.error(f"Error creating accessible text input: {e}")
        return st.text_input(label, value=value, key=key)


def accessible_text_area(
    label: str,
    value: str = "",
    height: Optional[int] = None,
    max_chars: Optional[int] = None,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    placeholder: Optional[str] = None,
    aria_label: Optional[str] = None,
    required: bool = False
) -> str:
    """
    Create WCAG 2.1 Level A compliant text area

    Args:
        label: Label for the text area
        value: Default value
        height: Height in pixels
        max_chars: Maximum character limit
        key: Unique key for the text area
        help_text: Help text for accessibility
        placeholder: Placeholder text
        aria_label: ARIA label (defaults to label)
        required: Whether field is required

    Returns:
        Text area value
    """
    try:
        # Enhanced label with required indicator
        enhanced_label = f"{label}{'*' if required else ''}"

        if help_text:
            st.markdown(f"**{enhanced_label}**")
            st.markdown(f"*{help_text}*")

        # Create text area
        text_value = st.text_area(
            enhanced_label,
            value=value,
            height=height,
            max_chars=max_chars,
            key=key,
            help=help_text,
            placeholder=placeholder
        )

        # Add accessibility attributes
        if key:
            aria_label_attr = aria_label or label
            required_attr = "true" if required else "false"

            aria_script = f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const textarea = document.querySelector('textarea');
                if (textarea) {{
                    textarea.setAttribute('aria-label', '{aria_label_attr}');
                    textarea.setAttribute('aria-required', '{required_attr}');
                }}
            }});
            </script>
            """
            st.markdown(aria_script, unsafe_allow_html=True)

        # Validation for required fields
        if required and not text_value.strip():
            st.markdown(
                '<div class="accessibility-error" role="alert" aria-live="polite">'
                f'⚠️ {label} é obrigatório</div>',
                unsafe_allow_html=True
            )

        return text_value

    except Exception as e:
        logger.error(f"Error creating accessible text area: {e}")
        return st.text_area(label, value=value, key=key)


def create_skip_links(targets: List[Dict[str, str]]):
    """
    Create skip navigation links (WCAG 2.4.1)

    Args:
        targets: List of dictionaries with 'href' and 'text' keys
    """
    try:
        skip_links_html = '<div class="skip-links">'

        for target in targets:
            href = target.get('href', '#')
            text = target.get('text', 'Pular seção')
            skip_links_html += f'<a href="{href}" class="skip-link">{text}</a>'

        skip_links_html += '</div>'

        st.markdown(skip_links_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error creating skip links: {e}")


def create_aria_landmark(
    content: str,
    role: str = "region",
    aria_label: str = "",
    element_id: str = ""
):
    """
    Create ARIA landmark (WCAG 1.3.1)

    Args:
        content: HTML content
        role: ARIA role
        aria_label: ARIA label
        element_id: Element ID
    """
    try:
        id_attr = f' id="{element_id}"' if element_id else ''
        label_attr = f' aria-label="{aria_label}"' if aria_label else ''

        landmark_html = f'<div role="{role}"{id_attr}{label_attr}>{content}</div>'

        st.markdown(landmark_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error creating ARIA landmark: {e}")


def accessible_metric(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    aria_label: Optional[str] = None
):
    """
    Create WCAG 2.1 Level A compliant metric display

    Args:
        label: Metric label
        value: Metric value
        delta: Change value
        delta_color: Color for delta
        help_text: Help text for accessibility
        aria_label: ARIA label
    """
    try:
        # Create metric with accessibility enhancements
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )

        # Add ARIA label for screen readers
        aria_label_text = aria_label or f"{label}: {value}"
        if delta:
            aria_label_text += f", mudança: {delta}"

        # Screen reader announcement
        sr_html = f"""
        <div class="sr-only" aria-live="polite">
            {aria_label_text}
        </div>
        """

        st.markdown(sr_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error creating accessible metric: {e}")
        st.metric(label, value, delta, delta_color)


def accessible_expander(
    label: str,
    expanded: bool = False,
    aria_label: Optional[str] = None
):
    """
    Create WCAG 2.1 Level A compliant expander

    Args:
        label: Expander label
        expanded: Initially expanded state
        aria_label: ARIA label

    Returns:
        Streamlit expander context manager
    """
    try:
        # Create expander with accessibility attributes
        expander = st.expander(label, expanded=expanded)

        # Add ARIA attributes via JavaScript
        aria_label_attr = aria_label or f"Expandir seção: {label}"
        expanded_attr = "true" if expanded else "false"

        aria_script = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const expander = document.querySelector('[data-testid="expander"]');
            if (expander) {{
                const button = expander.querySelector('button');
                if (button) {{
                    button.setAttribute('aria-label', '{aria_label_attr}');
                    button.setAttribute('aria-expanded', '{expanded_attr}');
                    button.setAttribute('role', 'button');
                }}
            }}
        }});
        </script>
        """

        st.markdown(aria_script, unsafe_allow_html=True)

        return expander

    except Exception as e:
        logger.error(f"Error creating accessible expander: {e}")
        return st.expander(label, expanded=expanded)


def create_accessible_table(
    data,
    caption: str,
    summary: Optional[str] = None,
    headers: Optional[List[str]] = None
):
    """
    Create WCAG 2.1 Level A compliant table

    Args:
        data: Table data (DataFrame or dict)
        caption: Table caption
        summary: Table summary for screen readers
        headers: Column headers
    """
    try:
        # Display caption
        st.markdown(f"**{caption}**")

        if summary:
            st.markdown(f"*{summary}*")

        # Create accessible table using st.dataframe with enhancements
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=False
        )

        # Add table accessibility attributes via JavaScript
        table_script = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const table = document.querySelector('table');
            if (table) {{
                table.setAttribute('role', 'table');
                table.setAttribute('aria-label', '{caption}');

                // Add scope attributes to headers
                const headers = table.querySelectorAll('th');
                headers.forEach(header => {{
                    header.setAttribute('scope', 'col');
                }});

                // Add table summary if provided
                if ('{summary}') {{
                    const captionElement = document.createElement('caption');
                    captionElement.textContent = '{caption}';
                    captionElement.className = 'sr-only';
                    table.insertBefore(captionElement, table.firstChild);
                }}
            }}
        }});
        </script>
        """

        st.markdown(table_script, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error creating accessible table: {e}")
        st.dataframe(data)


def announce_page_change(page_name: str):
    """
    Announce page changes to screen readers

    Args:
        page_name: Name of the new page
    """
    try:
        announcement = f"Página carregada: {page_name}"

        announcement_html = f"""
        <div aria-live="polite" aria-atomic="true" class="sr-only">
            {announcement}
        </div>
        """

        st.markdown(announcement_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error announcing page change: {e}")


def create_accessible_alert(
    message: str,
    alert_type: str = "info",
    dismissible: bool = False
):
    """
    Create WCAG 2.1 Level A compliant alert

    Args:
        message: Alert message
        alert_type: Type of alert (info, warning, error, success)
        dismissible: Whether alert can be dismissed
    """
    try:
        # Map alert types to appropriate ARIA roles and styling
        alert_config = {
            "info": {"role": "status", "icon": "ℹ️", "class": "info"},
            "warning": {"role": "alert", "icon": "⚠️", "class": "warning"},
            "error": {"role": "alert", "icon": "❌", "class": "error"},
            "success": {"role": "status", "icon": "✅", "class": "success"}
        }

        config = alert_config.get(alert_type, alert_config["info"])

        # Create alert with proper ARIA attributes
        alert_html = f"""
        <div role="{config['role']}"
             aria-live="polite"
             aria-atomic="true"
             class="accessibility-alert {config['class']}">
            {config['icon']} {message}
        </div>
        """

        st.markdown(alert_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error creating accessible alert: {e}")
        st.info(message)  # Fallback to standard Streamlit info