import os
from database import mark_clip_downloaded, query_clips
import streamlit as st
from twitch_downloader import download_clip

st.set_page_config(
    page_title="Marvel Rivals Clip Library",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎬 Marvel Rivals Clip Library")

# Sidebar Controls
st.sidebar.header("Filter & Search")
search_term = st.sidebar.text_input("Search (Title, Streamer, Clipper)")
downloaded_only = st.sidebar.checkbox("Show Downloaded Only", value=False)
sort_by = st.sidebar.selectbox(
    "Sort By",
    ["Views (High to Low)", "Newest First", "Duration (Longest)"],
    index=0,
)

sort_map = {
    "Views (High to Low)": "view_count DESC",
    "Newest First": "created_at DESC",
    "Duration (Longest)": "duration DESC",
}

# Fetch filtered records
clips = query_clips(
    search_term=search_term,
    downloaded_only=downloaded_only,
    order_by=sort_map[sort_by],
)

st.sidebar.metric("Clips Found", len(clips))

if not clips:
    st.info("No clips match your query or the database is empty.")
else:
    # 2-column grid layout
    cols = st.columns(2)
    for idx, clip in enumerate(clips):
        with cols[idx % 2]:
            st.subheader(clip["title"])
            st.caption(
                f"Streamer: **{clip['broadcaster_name']}** | "
                f"Clipped by: **{clip['creator_name']}** | "
                f"Views: **{clip['view_count']:,}** | "
                f"Length: **{round(clip['duration'], 1)}s**"
            )

            # Local video player vs thumbnail preview
            if clip["is_downloaded"] and os.path.exists(
                clip.get("file_path") or ""
            ):
                st.video(clip["file_path"])
                st.success(f"Downloaded: `{clip['file_path']}`")
            else:
                st.image(clip["thumbnail_url"], use_container_width=True)
                if st.button("⬇ Download Clip", key=f"dl_{clip['id']}"):
                    with st.spinner("Downloading direct MP4..."):
                        path = download_clip(
                            slug=clip["id"],
                            title=clip["title"],
                            thumbnail_url=clip["thumbnail_url"],
                        )
                        if path:
                            mark_clip_downloaded(clip["id"], path)
                            st.rerun()
                        else:
                            st.error("Failed to retrieve direct stream URL.")

            st.divider()
