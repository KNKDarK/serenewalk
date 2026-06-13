import streamlit as st
from typing import Optional
from i18n.translator import t

def inject_accessibility_css():
    st.markdown("""
    <style>
    /* Skip to content link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #000;
        color: #fff;
        padding: 8px 16px;
        z-index: 10000;
        text-decoration: none;
        font-weight: bold;
    }
    .skip-link:focus {
        top: 0;
    }

    /* Focus indicators - high contrast */
    *:focus {
        outline: 3px solid #FF6B35 !important;
        outline-offset: 2px;
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .stMarkdown {
            color: #000 !important;
        }
        .stButton > button {
            border: 2px solid #000 !important;
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Screen reader only text */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    /* Larger touch targets for mobile/accessibility */
    .stButton > button {
        min-height: 44px;
        min-width: 44px;
    }

    /* Improved color contrast for text */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        line-height: 1.6;
    }

    /* Emergency banner high contrast */
    .emergency-banner {
        background-color: #D32F2F;
        color: #FFFFFF;
        padding: 12px 16px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 1.1em;
    }

    /* Status indicators with icons for colorblind users */
    .status-ok::before { content: "✅ "; }
    .status-warn::before { content: "⚠️ "; }
    .status-error::before { content: "❌ "; }
    </style>
    """, unsafe_allow_html=True)

def create_accessible_header(text: str, level: int = 1, aria_level: Optional[int] = None):
    tag = f"h{level}"
    aria = f' role="heading" aria-level="{aria_level or level}"'
    st.markdown(f'<{tag}{aria}>{text}</{tag}>', unsafe_allow_html=True)

def create_accessible_text_input(
    label: str,
    key: str,
    placeholder: str = "",
    help_text: Optional[str] = None,
    aria_label: Optional[str] = None,
    height: Optional[int] = None
):
    aria = aria_label or label
    if height:
        return st.text_area(
            label,
            key=key,
            placeholder=placeholder,
            help=help_text,
            height=height,
            label_visibility="visible"
        )
    else:
        return st.text_input(
            label,
            key=key,
            placeholder=placeholder,
            help=help_text,
            label_visibility="visible"
        )

def create_accessible_button(label: str, key: Optional[str] = None, button_type: str = "secondary", use_container_width: bool = False):
    return st.button(
        label,
        key=key,
        type=button_type,
        use_container_width=use_container_width
    )

def create_language_selector():
    from i18n.translator import translator

    languages = translator.get_available_languages()
    current_lang = translator.get_language()

    lang_options = {lang["native"]: lang["code"] for lang in languages}
    current_native = next(
        (lang["native"] for lang in languages if lang["code"] == current_lang),
        "English"
    )

    selected = st.selectbox(
        label=t("accessibility.language_selector"),
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_native),
        key="language_selector",
        label_visibility="collapsed"
    )

    new_lang = lang_options[selected]
    if new_lang != current_lang:
        translator.set_language(new_lang)
        st.rerun()

def announce_to_screenreader(message: str):
    st.markdown(
        f'<div role="status" aria-live="polite" class="sr-only">{message}</div>',
        unsafe_allow_html=True
    )

def create_result_card(
    title: str,
    content: str,
    severity: Optional[str] = None,
    icon: Optional[str] = None
):
    severity_colors = {
        "emergency": "#D32F2F",
        "high": "#F57C00",
        "moderate": "#FBC02D",
        "low": "#388E3C"
    }
    color = severity_colors.get(severity, "#1976D2") if severity else "#1976D2"
    icon_prefix = icon or ("🚨" if severity == "emergency" else "ℹ️")

    st.markdown(f"""
    <div role="article" aria-label="{title}" style="
        border-left: 4px solid {color};
        padding: 12px 16px;
        margin: 8px 0;
        background-color: #f8f9fa;
        border-radius: 0 4px 4px 0;
    ">
        <strong>{icon_prefix} {title}</strong><br/>
        {content}
    </div>
    """, unsafe_allow_html=True)

def create_accessible_sidebar():
    with st.sidebar:
        st.markdown(f'<div role="complementary">', unsafe_allow_html=True)
        create_language_selector()
        st.divider()

def close_accessible_sidebar():
    st.markdown('</div>', unsafe_allow_html=True)
