import streamlit as st
import preprocessor
import helper # <-- FIXED: Corrected typo from 'hepler' to 'helper'
import matplotlib.pyplot as plt
import plotly.express as px  
import seaborn as sns

# --- FONT FIX START (Final attempt for font compatibility) ---
# We prioritize the system's default sans-serif and use a large list of 
# emoji-supporting fonts as fallbacks.
try:
    plt.rcParams['font.family'] = 'sans-serif'
    # Adding a massive list of known emoji-supporting fonts to increase the chance of success
    plt.rcParams['font.sans-serif'] = [
        'Noto Color Emoji', 'Segoe UI Emoji', 'Apple Color Emoji', 'EmojiOne',
        'DejaVu Sans', 'Arial Unicode MS', 'sans-serif'
    ] 
    plt.rcParams['font.size'] = 10 # Standard font size
    
except Exception as e:
    st.error(f"Error setting font: {e}")
    plt.rcParams['font.family'] = 'sans-serif' 
# --- FONT FIX END ---

st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    
    # Safely remove 'group_notification' regardless of capitalization
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    if 'Group_notification' in user_list:
        user_list.remove('Group_notification')
    
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show Analysis With Respect To",user_list)
    
    # --- START OF ANALYSIS BLOCK ---
    if st.sidebar.button("SHOW ANALYSIS"):
        
        # 1. TOP STATISTICS
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("TOP STATISTICS")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Total Links Shared")
            st.title(num_links)

        # 2. MONTHLY TIMELINE
        st.title('Monthly Timeline')
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['messages'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # 3. DAILY TIMELINE
        st.title('Daily Timeline')
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['messages'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # 4. ACTIVITY MAP
        st.title('Activity Map')
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most Busy Month")
            busy_day = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # 5. WEEKLY ACTIVITY HEATMAP
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # 6. MOST BUSY USERS (Overall only)
        if selected_user == "Overall":
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_user(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='r')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # 7. WORD CLOUD
        st.title("Word Cloud")
        df_wc = helper.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # 8. MOST COMMON WORDS
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.title("Most Common Words")
        st.pyplot(fig)
        
        # 9. EMOJI ANALYSIS <-- THIS SECTION IS NOW CORRECTLY INDENTED
        
        # The user had this line twice, but we only need the one at the top.
        # import plotly.express as px  
        
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig = px.pie(
                emoji_df.head(),
                values=1,         # column containing counts
                names=0,          # column containing emojis
                title="Emoji Distribution",
            )
            st.plotly_chart(fig)
        # --- END OF EMOJI ANALYSIS (Line 134 in your original traceback) ---
        
    # --- END OF ANALYSIS BLOCK ---
