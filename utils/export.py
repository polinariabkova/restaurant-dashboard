"""
Export utilities — one-click PDF / Excel report generation per industry.

Uses session_state to accumulate figures and DataFrames as the page renders,
then generates a downloadable file when the user clicks a sidebar button.
"""

import io
import datetime
from typing import Dict, List, Optional, Any

import streamlit as st
import pandas as pd

# ── Session-state helpers ─────────────────────────────────────────────────

def _init_export_state():
    """Ensure session_state has the export bucket."""
    if "export_figures" not in st.session_state:
        st.session_state["export_figures"] = []   # list of (title, fig)
    if "export_tables" not in st.session_state:
        st.session_state["export_tables"] = []    # list of (title, DataFrame)
    if "export_metrics" not in st.session_state:
        st.session_state["export_metrics"] = []   # list of (label, value, delta)


def reset_export_state():
    """Clear accumulated export data (call at top of each page render)."""
    st.session_state["export_figures"] = []
    st.session_state["export_tables"] = []
    st.session_state["export_metrics"] = []


def add_export_figure(title: str, fig):
    """Register a Plotly figure for export."""
    _init_export_state()
    st.session_state["export_figures"].append((title, fig))


def add_export_table(title: str, df: pd.DataFrame):
    """Register a DataFrame for export."""
    _init_export_state()
    if df is not None and not df.empty:
        st.session_state["export_tables"].append((title, df))


def add_export_metric(label: str, value: str, delta: str = ""):
    """Register a metric card value for export."""
    _init_export_state()
    st.session_state["export_metrics"].append((label, value, delta))


# ── Excel generation ──────────────────────────────────────────────────────

def generate_excel_report(industry_name: str) -> io.BytesIO:
    """Build an Excel workbook from accumulated export data."""
    _init_export_state()
    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # --- Summary sheet ---
        summary_rows = [
            {"Metric": "Industry", "Value": industry_name},
            {"Metric": "Report Date", "Value": datetime.date.today().strftime("%B %d, %Y")},
        ]
        for label, value, delta in st.session_state["export_metrics"]:
            row = {"Metric": label, "Value": value}
            if delta:
                row["Change"] = delta
            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # Auto-fit summary columns
        ws = writer.sheets["Summary"]
        for col_cells in ws.columns:
            max_len = max(len(str(c.value or "")) for c in col_cells) + 2
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len, 50)

        # --- Data sheets ---
        for title, df in st.session_state["export_tables"]:
            # Excel sheet names max 31 chars, no special chars
            safe_name = title[:31].replace("/", "-").replace("\\", "-").replace(":", "-")
            # Avoid duplicate sheet names
            existing = [s for s in writer.sheets]
            if safe_name in existing:
                safe_name = safe_name[:28] + "_2"
            try:
                df.to_excel(writer, sheet_name=safe_name, index=True)
                ws = writer.sheets[safe_name]
                for col_cells in ws.columns:
                    max_len = max(len(str(c.value or "")) for c in col_cells) + 2
                    ws.column_dimensions[col_cells[0].column_letter].width = min(max_len, 40)
            except Exception:
                pass

        # --- Charts sheet (images) ---
        try:
            import kaleido  # noqa: F401
            from openpyxl.drawing.image import Image as XlImage

            if st.session_state["export_figures"]:
                chart_ws = writer.book.create_sheet("Charts")
                row_pos = 1
                for title, fig in st.session_state["export_figures"]:
                    try:
                        img_bytes = fig.to_image(format="png", width=900, height=450,
                                                  scale=2, engine="kaleido")
                        img_buf = io.BytesIO(img_bytes)
                        img = XlImage(img_buf)
                        chart_ws.cell(row=row_pos, column=1, value=title)
                        chart_ws.add_image(img, f"A{row_pos + 1}")
                        row_pos += 28  # ~450px / 15px per row ≈ 30 rows
                    except Exception:
                        chart_ws.cell(row=row_pos, column=1,
                                      value=f"{title} — chart image unavailable")
                        row_pos += 2
        except ImportError:
            pass  # kaleido not available, skip chart images

    buf.seek(0)
    return buf


# ── PDF generation ────────────────────────────────────────────────────────

def generate_pdf_report(industry_name: str) -> io.BytesIO:
    """Build a PDF report from accumulated export data."""
    from fpdf import FPDF
    _init_export_state()

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Cover page ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 40, "", ln=True)  # top spacer
    pdf.cell(0, 15, f"{industry_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 12, "Industry Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Generated {datetime.date.today().strftime('%B %d, %Y')}",
             ln=True, align="C")
    pdf.cell(0, 8, "Polina's Portfolio Tracker", ln=True, align="C")

    # ── Metrics summary ──
    metrics = st.session_state["export_metrics"]
    if metrics:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Key Metrics", ln=True)
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 11)

        # Table header
        col_w = [100, 80, 60]
        pdf.set_fill_color(13, 43, 85)  # #0D2B55
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(col_w[0], 8, "Metric", border=1, fill=True)
        pdf.cell(col_w[1], 8, "Value", border=1, fill=True)
        pdf.cell(col_w[2], 8, "Change", border=1, fill=True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        for label, value, delta in metrics:
            pdf.cell(col_w[0], 7, str(label)[:60], border=1)
            pdf.cell(col_w[1], 7, str(value)[:40], border=1)
            pdf.cell(col_w[2], 7, str(delta)[:30], border=1)
            pdf.ln()

    # ── Chart pages ──
    has_kaleido = True
    try:
        import kaleido  # noqa: F401
    except ImportError:
        has_kaleido = False

    if has_kaleido:
        for title, fig in st.session_state["export_figures"]:
            try:
                img_bytes = fig.to_image(format="png", width=1200, height=500,
                                          scale=2, engine="kaleido")
                img_buf = io.BytesIO(img_bytes)

                # Save to temp file (fpdf2 needs a file path or name)
                import tempfile, os
                tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                tmp.write(img_bytes)
                tmp.close()

                pdf.add_page()
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, title, ln=True)
                pdf.image(tmp.name, x=10, y=25, w=270)

                os.unlink(tmp.name)
            except Exception:
                pdf.add_page()
                pdf.set_font("Helvetica", "", 12)
                pdf.cell(0, 10, f"{title} — chart unavailable", ln=True)

    # ── Data tables ──
    for title, df in st.session_state["export_tables"]:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.ln(2)

        # Limit columns for readability
        cols = list(df.columns)[:8]
        df_show = df[cols].head(30)

        col_count = len(cols)
        col_w = min(270 // max(col_count, 1), 60)

        # Header
        pdf.set_fill_color(13, 43, 85)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        for c in cols:
            pdf.cell(col_w, 6, str(c)[:20], border=1, fill=True)
        pdf.ln()

        # Rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 7)
        for _, row in df_show.iterrows():
            for c in cols:
                val = row[c]
                if isinstance(val, float):
                    txt = f"{val:,.2f}"
                else:
                    txt = str(val)[:20]
                pdf.cell(col_w, 5, txt, border=1)
            pdf.ln()

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf


# ── Sidebar export buttons ────────────────────────────────────────────────

def render_export_sidebar(industry_name: str):
    """Render download buttons in the sidebar for Excel and PDF export."""
    _init_export_state()

    with st.sidebar:
        st.divider()
        st.subheader("Export Report")
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        safe_industry = industry_name.replace(" ", "_").replace("&", "and")

        col1, col2 = st.columns(2)
        with col1:
            try:
                excel_buf = generate_excel_report(industry_name)
                st.download_button(
                    label="Download Excel",
                    data=excel_buf,
                    file_name=f"{safe_industry}_Report_{date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Excel error: {e}")

        with col2:
            try:
                pdf_buf = generate_pdf_report(industry_name)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buf,
                    file_name=f"{safe_industry}_Report_{date_str}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")
