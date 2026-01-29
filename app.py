import streamlit as st
import whatsapp_preprocessor as preprocessor
import helper
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# Set Page Config for a professional look
st.set_page_config(page_title="WhatsApp Analytics", page_icon="💬", layout="wide")

# Font handling for emojis
matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'

# Custom CSS for polished UI
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
        border-bottom: 2px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg", width=50)
    st.title("Chat Analyzer")
    st.markdown("Extract insights from your exported conversations.")
    st.divider()
    
    uploaded_file = st.file_uploader("📁 Upload WhatsApp Chat (.txt)", type=["txt"])
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        # fetch unique users
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.selectbox("👤 Select User", user_list)
        show_analysis = st.button("🚀 Run Analysis", use_container_width=True, type="primary")

# ---------------- MAIN CONTENT ----------------
if uploaded_file is not None:
    if show_analysis:
        # Fetch stats
        num_messages, words, num_media_messages, links = helper.fetch_stats(selected_user, df)

        # ---------------- TABS ----------------
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 OVERVIEW",
            "👥 USERS",
            "🧠 TEXT",
            "😄 EMOJIS",
            "🗺️ ACTIVITY"
        ])

        # ================= TAB 1: OVERVIEW =================
        with tab1:
            st.markdown("### 📈 Quick Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("💬 Messages", f"{num_messages:,}")
            with col2: st.metric("📝 Total Words", f"{words:,}")
            with col3: st.metric("🖼️ Media Files", f"{num_media_messages:,}")
            with col4: st.metric("🔗 Links Shared", f"{links:,}")

            st.divider()

            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("#### 📆 Monthly Engagement")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(timeline['time'], timeline['message'], color='#25D366', linewidth=2, marker='o', markersize=4)
                plt.xticks(rotation='vertical', fontsize=8)
                ax.set_facecolor('#f8f9fa')
                st.pyplot(fig)

            with col_right:
                st.markdown("#### 🗓 Daily Volume")
                daily = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(daily['date'], daily['message'], color='#7d3cff', linewidth=1.5)
                plt.xticks(rotation='vertical', fontsize=8)
                ax.set_facecolor('#f8f9fa')
                st.pyplot(fig)

        # ================= TAB 2: USERS =================
        with tab2:
            if selected_user == "Overall":
                st.markdown("### 🏆 Leaderboard: Most Active Users")
                x, percent_df = helper.most_busy_users(df)
                
                col1, col2 = st.columns([3, 2])
                with col1:
                    fig, ax = plt.subplots()
                    sns.barplot(x=x.index, y=x.values, palette="viridis", ax=ax)
                    plt.xticks(rotation='vertical')
                    ax.set_ylabel("Messages Sent")
                    st.pyplot(fig)

                with col2:
                    st.markdown("#### Percentage Contribution")
                    st.dataframe(percent_df.style.background_gradient(cmap='Blues'), use_container_width=True)
            else:
                st.info(f"Showing detailed profile for: **{selected_user}**")

        # ================= TAB 3: TEXT ANALYSIS =================
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ☁️ Word Cloud")
                wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)

            with col2:
                st.markdown("#### 🔝 Top 20 Frequently Used Words")
                common_words = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots()
                sns.barplot(x=common_words['count'], y=common_words['word'], palette="rocket", ax=ax)
                st.pyplot(fig)

        # ================= TAB 4: EMOJIS =================
        with tab4:
            emoji_df = helper.emoji_analysis(selected_user, df)
            st.markdown("### 😄 Emoji Breakdown")

            if emoji_df.shape[0] > 0:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(emoji_df.head(10), use_container_width=True)
                with col2:
                    pie_df = emoji_df.head(6)
                    fig, ax = plt.subplots()
                    ax.pie(pie_df['count'], labels=pie_df['emoji'], autopct='%1.1f%%', 
                           startangle=140, colors=sns.color_palette("pastel"))
                    st.pyplot(fig)
            else:
                st.info("No emojis detected in this chat.")

        # ================= TAB 5: ACTIVITY MAP =================
        with tab5:
            busy_day, busy_month, heatmap_data = helper.activity_map(selected_user, df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📅 Busy Days")
                fig, ax = plt.subplots()
                sns.barplot(x=busy_day.index, y=busy_day.values, palette="coolwarm", ax=ax)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.markdown("#### 🌙 Busy Months")
                fig, ax = plt.subplots()
                sns.barplot(x=busy_month.index, y=busy_month.values, palette="magma", ax=ax)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.markdown("#### 🔥 Hourly Activity Heatmap")
            fig, ax = plt.subplots(figsize=(15, 6))
            sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, cbar=True, ax=ax)
            st.pyplot(fig)

else:
    # Landing state
    st.info("Please upload a WhatsApp chat file (.txt) from the sidebar to begin analysis.")
    st.markdown("""
    **How to get the chat file?**
    1. Open WhatsApp on your phone.
    2. Open a chat or group.
    3. Tap 'More options' (three dots) > More > Export chat.
    4. Choose **Without Media**.
    5. Upload the generated .txt file here!
    """)