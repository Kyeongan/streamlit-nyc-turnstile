import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import datetime
import streamlit as st
st.set_page_config(
    page_title="NYC MTA Turnstile Traffic Dashboard",
    page_icon="🚊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Kyeongan/streamlit-nyc-turnstile',
        'Report a bug': "https://github.com/Kyeongan/streamlit-nyc-turnstile/issues"
    }
)


st.markdown("""
<style>
html {
  font-size: 0.9rem;
}
[data-testid="stMarkdownContainer"]>p {
    font-size: 1.2rem;
}
[data-testid="stMetricValue"] {
    font-size: 6.0rem;
    font-weight: 200;
    color: #2980b9;
}
.big-font {
    font-size:1.8rem !important;
    font-weight: 600;
}
.mid-font {
    font-size: 1.5rem !important;
    font-weight: 600;
    margin-top: 50px;
    color: #2d3436;
}
</style>
""", unsafe_allow_html=True)


st.title("NYC MTA Turnstile Traffic Dashboard")
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("About Data")
    st.caption("This dashboard uses MTA turnstile usage data between January 1st 2020 and June 30th, 2020 for the New York Subway system and it is available at http://web.mta.info/developers/turnstile.html")

with col_right:
    # st.subheader("NYC MTA Turnstile")
    st.image("https://miro.medium.com/v2/resize:fit:1400/format:webp/1*GnEQe-mNGgGxSaMCQqS28A.jpeg", width=350)

num_weeks = 1

# @st.cache_data
def load_data():
    filelist = []
    startdate = pd.Timestamp('2020-01-04 00:00:00')
    filename_regex = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt"
    for numfiles in range(num_weeks):

        # create the appropriate filename for the week
        startdate_str = str(
            startdate.year)[-2:] + str(startdate.month).zfill(2) + str(startdate.day).zfill(2)
        filename = filename_regex.format(startdate_str)

        # read the file and append it to the list of files to be concatenated
        df = pd.read_csv(filename, parse_dates=['DATE'])
        filelist.append(df)

        # advance to the next week
        startdate += pd.Timedelta(days=7)

    df = pd.concat(filelist, axis=0, ignore_index=True)

    return df


# ==========================================================
# ========== SIDEBAR config here ==========
# ==========================================================
with st.sidebar:
    st.write("Please Filter Here:")
    num_weeks = st.slider('Period (Week)', 1, 10)
    # st.write("", num_weeks, 'weeks selected')

    # st.title("Below are work-in-progress")
    # st.title("")

    # st.title("")
    # start_time = st.slider(
    #     "When do you start?",
    #     value=datetime.date(2020, 1, 1),
    #     format="MM/DD/YYYY")
    # st.write("Start date:", start_time)

    # st.title("")
    # d = st.date_input(
    #     "",
    #     datetime.date(2020, 1, 1),
    # )

    # st.title("")
    # st.title("")
    # st.title("")
    # st.title("")
    st.write(
        'Created by Karl Kwon @ [GitHub](https://github.com/Kyeongan)')


# comment/uncomment below for the test
df = load_data()
st.write(df.shape[0])

df.groupby(['UNIT', 'SCP'])['STATION'].nunique().sort_values()
df.sort_values(by=['DATE', 'TIME'])  # checking start/end of date/time
df['TIME'] = pd.to_datetime(df['TIME'], format='%H:%M:%S').dt.time
df = df.sort_values(by=['UNIT', 'SCP', 'DATE', 'TIME'])


df.columns = [column.strip() for column in df.columns]
# strip column names of blank spaces

df['ENTRY_DELTA'] = df['ENTRIES'].diff()
df['EXIT_DELTA'] = df['EXITS'].diff()
# Finding the difference in values between consecutive rows to find out traffic flow between timings


# data between Jan 1, 2020 to Jun 30th, 2020
df = df[df['DATE'] >= pd.Timestamp('2020-01-01 00:00:00')]

df['ENTRY_DELTA'][df['ENTRY_DELTA'] > 10000] = np.nan
df['ENTRY_DELTA'][df['ENTRY_DELTA'] < 0] = np.nan
df['EXIT_DELTA'][df['EXIT_DELTA'] > 10000] = np.nan
df['EXIT_DELTA'][df['EXIT_DELTA'] < 0] = np.nan


df.reset_index(inplace=True)

df.drop('index', axis=1, inplace=True)

delta_list = list(df['ENTRY_DELTA'])
ind = 0
for i in delta_list:
    if np.isnan(i) == 1:
        delta_list[ind] = np.nanmean(
            [delta_list[ind-2], delta_list[ind-1], delta_list[ind+1], delta_list[ind+2]])
    ind += 1

df['ENTRY_DELTA_1'] = delta_list
# for each NaN values, replace it with the mean of values before and after the NaN value

df['ENTRY_DELTA_1'].isnull().sum()
# check for any NaN values remaining

delta_list = list(df['EXIT_DELTA'])
ind = 0
for i in delta_list:
    if np.isnan(i) == 1:
        delta_list[ind] = np.nanmean([delta_list[ind-1], delta_list[ind+1]])
    ind += 1

df['EXIT_DELTA_1'] = delta_list
# for each NaN values, replace it with the mean of values before and after the NaN value

df['EXIT_DELTA_1'].isnull().sum()
# check for any NaN values remaining

df['ENTRY_EXIT'] = df['ENTRY_DELTA_1'] + df['EXIT_DELTA_1']
# find out the total traffic from entry and exit between each timing

group_station = df.groupby(
    'STATION')['ENTRY_EXIT'].sum().sort_values(ascending=False)
# Checking the top 10 station for traffic in the week 22/8/20 to 28/8/20


# st.subheader("Top 10 busiest stations of the New York City Subway")
st.markdown('<p class="mid-font">Top 10 busiest stations of the New York City Subway</p>',
            unsafe_allow_html=True)
max = group_station.max()
steps = np.ceil(max/10)
st.write(max)
fig = plt.figure(figsize=[8, 3])
ax = sns.barplot(data=group_station.head(10).reset_index(),
                 x='ENTRY_EXIT', y='STATION', palette='rainbow')
plt.xlabel('Total Traffic', weight='bold')
plt.ylabel('', weight='bold', fontsize=15)
plt.title('', fontsize='13', weight='bold')
plt.xticks(range(0, int(max*1.2), int(steps)), [
           str(int(i/1000))+'k' for i in range(0, int(max*1.2), int(steps))])
for p in ax.patches:
    ax.annotate(' '+str(+int(p.get_width()/1000))+'k',
                (p.get_width(), p.get_y()+0.5))

st.pyplot(fig)


def millions(x, pos):
    """The two args are the value and tick position."""
    return '{:1.1f}M'.format(x*1e-6)


# st.subheader("Station traffic in the week")
st.markdown('<p class="mid-font">Station traffic in the week</p>',
            unsafe_allow_html=True)
df_10 = df[df['STATION'].isin(list(group_station.head(10).index))]
df_10['WEEKDAY'] = df_10['DATE'].dt.day_name()
group_station_day = df_10.groupby(['STATION', 'WEEKDAY'])[
    'ENTRY_EXIT'].sum()

matrix_station_day = group_station_day.unstack()
matrix_station_day.reset_index()
matrix_station_day = matrix_station_day.reindex(
    columns=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
matrix_station_day = matrix_station_day.reindex(
    index=list(group_station.head(10).index))
matrix_station_day.applymap(lambda x: str(round(x/1000, 1))+'k')
array = np.array(matrix_station_day.applymap(
    lambda x: str(round(x/1000, 1))+'k'))

fig = plt.figure(figsize=[10, 10])
cmap = sns.cubehelix_palette(light=1, as_cmap=True)
ax2 = sns.heatmap(matrix_station_day, cmap='Blues',
                  linecolor='white', linewidths=1, annot=array, fmt='')
plt.xlabel('', fontsize=15)
plt.ylabel('', fontsize=15)
plt.title('', weight='bold', fontsize=15)
# plt.savefig('heatmap1.png', transparent=True, bbox_inches='tight')
# Creating heatmap of traffic a day in the top 10 stations.
# Trends reveal that traffic is higher on weekdays compared with weekends
st.pyplot(fig)


st.subheader("")
st.markdown('<p class="mid-font">Traffic based on day and time period</p>',
            unsafe_allow_html=True)


def timeperiod(time):
    if time >= datetime.time(0, 0, 0) and time < datetime.time(4, 0, 0):
        return "12am-4am"
    elif time >= datetime.time(4, 0, 0) and time < datetime.time(8, 0, 0):
        return "4am-8am"
    elif time >= datetime.time(8, 0, 0) and time < datetime.time(12, 0, 0):
        return "8am-12pm"
    elif time >= datetime.time(12, 0, 0) and time < datetime.time(16, 0, 0):
        return "12pm-4pm"
    elif time >= datetime.time(16, 0, 0) and time < datetime.time(20, 0, 0):
        return "4pm-8pm"
    else:
        return "8pm-12am"


df_10['TIME_PERIOD'] = df_10['TIME'].apply(timeperiod)

matrix_list = []
for station in list(group_station.head(10).index):
    df_station = df_10[df_10['STATION'] == station]
    group_day_time = df_station.groupby(['WEEKDAY', 'TIME_PERIOD'])[
        'ENTRY_EXIT'].sum()
    matrix_day_time = group_day_time.unstack()
    matrix_day_time.reset_index()
    matrix_day_time = matrix_day_time.reindex(
        index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    matrix_day_time = matrix_day_time.reindex(
        columns=["12am-4am", "4am-8am", "8am-12pm", "12pm-4pm", "4pm-8pm", "8pm-12am"])
    matrix_list.append(matrix_day_time)

fig, axn = plt.subplots(2, 5, sharex=True, sharey=True, figsize=(15, 6))
cmap = sns.cubehelix_palette(light=1, as_cmap=True)
cbar_ax = fig.add_axes([.91, .3, .03, .4])

for i, ax in enumerate(axn.flat):
    station = matrix_list[i]
    sns.heatmap(station, ax=ax, cmap=cmap,
                cbar=i == 0,
                cbar_ax=None if i else cbar_ax,
                linecolor='white', linewidths=0.5)
    ax.set_title(list(group_station.head(10).index)[i])
    ax.set_xlabel('')
    ax.set_ylabel('')
    # Creating heatmap of traffic based on day and time period for each of the 10 stations
    # Trend shows that traffic is heavier in the late afternoon and evening periods, even during weekdays
    # The trend reveals that the Covid pandemic could have caused many companies to adopt WFH arrangements, thus eliminating morning rush hours.
    # The trend reveals that the street teams should deploy manpower to these stations from late afternoon to late evenings.

st.pyplot(fig)


st.subheader("")
st.markdown('<p class="mid-font">Net Entry/Exit of Commuters</p>',
            unsafe_allow_html=True)

df_10[(df_10['STATION'] == '34 ST-PENN STA') & (df_10['WEEKDAY'] ==
                                                'Friday') & (df_10['TIME_PERIOD'] == '4pm-8pm')]['ENTRY_EXIT'].mean()
# Check average traffic through a turnstile in 34 ST-PENN STATION on Friday at 4pm-8pm

df_10[(df_10['STATION'] == '34 ST-PENN STA') & (df_10['WEEKDAY'] ==
                                                'Friday') & (df_10['TIME_PERIOD'] == '4pm-8pm')]['ENTRY_EXIT'].count()
# Check number of turnstiles in 34 ST-PENN STATION

df_10['TRAFFIC_DELTA'] = df_10['ENTRY_DELTA_1'] - df_10['EXIT_DELTA_1']

matrix_list = []
for station in list(group_station.head(10).index):
    df_station = df_10[df_10['STATION'] == station]
    group_day_time = df_station.groupby(['WEEKDAY', 'TIME_PERIOD'])[
        'TRAFFIC_DELTA'].sum()
    matrix_day_time = group_day_time.unstack()
    matrix_day_time.reset_index()
    matrix_day_time = matrix_day_time.reindex(
        index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    matrix_day_time = matrix_day_time.reindex(
        columns=["12am-4am", "4am-8am", "8am-12pm", "12pm-4pm", "4pm-8pm", "8pm-12am"])
    matrix_list.append(matrix_day_time)

fig, axn = plt.subplots(2, 5, sharex=True, sharey=True, figsize=(15, 6))
cbar_ax = fig.add_axes([.91, .3, .03, .4])

for i, ax in enumerate(axn.flat):
    station = matrix_list[i]
    sns.heatmap(station, ax=ax, cmap='coolwarm',
                cbar=i == 0,
                cbar_ax=None if i else cbar_ax,
                linecolor='white', linewidths=0.5, vmin=-4000, vmax=4000)
    ax.set_title(list(group_station.head(10).index)[i])
    ax.set_xlabel('')
    ax.set_ylabel('')

st.pyplot(fig)
# Creating heatmap of traffic delta based on day and time period for each of the 10 stations
# Trend reveals stations which are in potential residential and commerical areas.
