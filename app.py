import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
import plotly.figure_factory as ff
import scipy
import helper
import preprocessor

# Verify scipy installation
print("scipy version:", scipy.__version__)

# Load data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

# Preprocess data
df = preprocessor.preprocess(df, region_df)

# Streamlit sidebar
st.sidebar.header("Olympics Analysis")
st.sidebar.image("https://yt3.googleusercontent.com/ytc/AIdro_mAox1Q3Td0BNFEkDJziicg4g1UaqS79iiOt6eawgE5UKNo=s900-c-k-c0x00ffffff-no-rj")
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
)

if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    if selected_year and selected_country:
        medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

        if selected_year == 'Overall' and selected_country == 'Overall':
            st.title('Overall Tally')
        elif selected_year != 'Overall' and selected_country == 'Overall':
            st.title(f"Medal Tally in {selected_year} Olympics")
        elif selected_year == 'Overall' and selected_country != 'Overall':
            st.title(f"{selected_country} Overall Performance in Olympics")
        else:
            st.title(f"{selected_country}'s Performance in {selected_year} Olympics")

        st.table(medal_tally)

elif user_menu == 'Overall Analysis':
    # Aggregate data for overall analysis
    editions = df['Year'].nunique()
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.title("Top Statistics")
    # Display overall analysis metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Athletes")
        st.title(athletes)
    with col3:
        st.header("Nations")
        st.title(nations)

    # Add a divider
    st.markdown("---")

    # Participating Nations over time
    nations_over_time = helper.participating_nations_over_time(df)
    fig = px.line(nations_over_time, x='Year', y='Number of Countries',
                  title='Participating Nations over the Years')
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig)
    st.markdown("---")

    # Occurring Events over time
    events_over_time = helper.events_over_time(df)
    fig1 = px.line(events_over_time, x='Year', y='Number of Events Occurred',
                   title='Number of Events over the Years')
    fig1.update_layout(title_x=0.5)
    st.plotly_chart(fig1)
    st.markdown("---")

    # Athletes participating over time
    athletes_over_time = helper.athletes_over_time(df)
    fig2 = px.line(athletes_over_time, x='Year', y='Athletes over the Years',
                   title='Number of Athletes over the Years')
    fig2.update_layout(title_x=0.5)
    st.plotly_chart(fig2)
    st.markdown("---")

    st.markdown("## Number of Events over Time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int),
        annot=True, ax=ax, cmap="YlGnBu")
    st.pyplot(fig)
    st.markdown("---")

    st.markdown("## Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a sport', sport_list)
    x = helper.most_successful_athletes(df, selected_sport)
    st.table(x)
    st.markdown("---")

if user_menu == 'Country-wise Analysis':
    st.sidebar.title("Medals Achieved by a Country over the Years")
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    country_df = helper.year_wise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal', title=f"{selected_country}'s Medal Tally over the Years")
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig)
    st.markdown("---")

    st.markdown(f"## {selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pt, annot=True, ax=ax, cmap="YlGnBu")
    st.pyplot(fig)
    st.markdown("---")

    st.markdown(f"## Top 10 Athletes of {selected_country}")
    top10_df = helper.country_wise_most_successful_athletes(df, selected_country)
    st.table(top10_df)
    st.markdown("---")

if user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, height=600, width=1000)
    st.markdown("## Distribution of Age")
    st.plotly_chart(fig)
    st.markdown("---")

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling',
                     'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens', 'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo',
                     'Cricket', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna().tolist())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, height=600, width=1000)
    st.markdown("## Distribution of Age in Famous sports(Gold Medalists)")
    st.plotly_chart(fig)
    st.markdown("---")

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    st.title("Height vs Weight Scatterplot")
    selected_sport = st.selectbox('Select a sport', sport_list)
    temp_df=helper.weight_v_height(df,selected_sport)

    fig,axis=plt.subplots()
    ax=sns.scatterplot(x=temp_df['Weight'],y=temp_df['Height'],hue=temp_df['Medal'],style=temp_df['Sex'],s=70)
    st.pyplot(fig)
    st.markdown("---")

    st.title("Men Vs Women Athletes over the years")
    temp_df=helper.men_vs_women(df)
    fig = px.line(temp_df, x="Year", y=["Male", "Female"])
    st.plotly_chart(fig)




