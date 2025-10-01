# --- Paste this into modules/home.py (e.g., bottom of dashboard_home_view) ---
from utils.digest import generate_digest_pdf

st.subheader("📄 Daily Digest")
if st.button("Generate Digest Now"):
    pdf = generate_digest_pdf()
    st.download_button("Download Daily Digest PDF", pdf, file_name="daily_digest.pdf", mime="application/pdf")
    st.success("Digest created")
