from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji
extract = URLExtract()

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    #fetch number of total messages
    num_messages = df.shape[0]

    #fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    #fetch number of media messages
    num_media_messages = df['message'].str.contains('Media omitted').sum()

    #fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
        
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # ❌ remove group notifications
    df = df[df['user'] != 'group_notification']

    # ❌ remove media messages
    df = df[~df['message'].str.contains('Media omitted', na=False)]

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white'
    )

    text = df['message'].str.cat(sep=" ")
    return wc.generate(text)

def most_common_words(selected_user, df, top_n=20):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # remove group notifications
    df = df[df['user'] != 'group_notification']

    # remove media messages
    df = df[~df['message'].str.contains('Media omitted', na=False)]

    words = []

    for message in df['message']:
        for word in message.lower().split():
            words.append(word)

    most_common_df = pd.DataFrame(
        Counter(words).most_common(top_n),
        columns=['word', 'count']
    )

    return most_common_df

def emoji_analysis(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(10),
        columns=['emoji', 'count']
    )

    return emoji_df

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = (
        df
        .groupby(['year', 'month'])
        .count()['message']
        .reset_index()
    )

    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily = (
        df
        .groupby('date')
        .count()['message']
        .reset_index()
    )

    return daily

def activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                 'Friday', 'Saturday', 'Sunday']

    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    busy_day = df['day_name'].value_counts().reindex(day_order)
    busy_month = df['month'].value_counts().reindex(month_order)

    heatmap_data = df.pivot_table(
        index='day_name',
        columns='hour',
        values='message',
        aggfunc='count'
    ).reindex(day_order).fillna(0)

    return busy_day, busy_month, heatmap_data
