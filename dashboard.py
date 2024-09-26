import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def plot_weekday_rentals(df):
    total_by_weekday = df.groupby('weekday')['total_users'].sum().reset_index()
    plt.figure(figsize=(6, 4))
    sns.barplot(data=total_by_weekday, x='weekday', y='total_users', palette='viridis')
    plt.title('Total Penyewa Sepeda Berdasarkan Hari')
    plt.xlabel('Hari (0=Senin, 6=Minggu)')
    plt.ylabel('Total Penyewa Sepeda')
    plt.xticks(ticks=range(0, 7), labels=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'])
    st.pyplot(plt.gcf())

def plot_hourly_rentals(df):
    total_by_hour = df.groupby('hr')['total_users'].sum().reset_index()
    plt.figure(figsize=(6, 4))
    sns.barplot(data=total_by_hour, x='hr', y='total_users', palette='viridis')
    plt.title('Total Penyewa Sepeda Berdasarkan Jam')
    plt.xlabel('Jam')
    plt.ylabel('Total Penyewa Sepeda')
    st.pyplot(plt.gcf())

def plot_hour_day_trend(total_by_hour_day):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=total_by_hour_day, x='hr', y='total_users', hue='weekday', palette='tab10')
    plt.title('Tren Penyewa Sepeda Berdasarkan Jam dan Hari')
    plt.xlabel('Jam dalam Sehari')
    plt.ylabel('Total Penyewa Sepeda')
    plt.xticks(range(0, 24))
    plt.legend(title='Hari dalam Seminggu', loc='upper right')
    st.pyplot(plt.gcf())

def plot_temp_humidity_heatmap(hour_df):
    pivot_table = hour_df.pivot_table(values='total_users', index='temp', columns='hum', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, cmap='coolwarm', annot=False, cbar_kws={'label': 'Jumlah Penyewa Sepeda'})
    plt.title('Hubungan Suhu, Kelembaban, dan Jumlah Penyewa Sepeda')
    plt.xlabel('Kelembaban (hum)')
    plt.ylabel('Suhu (temp)')
    st.pyplot(plt.gcf())

def plot_binned_hour_usage(hour_df):
    bins = [0, 5, 10, 14, 19, 24]
    labels = ['Malam', 'Pagi', 'Siang', 'Sore', 'Malam Akhir']
    hour_df['hour_bin'] = pd.cut(hour_df['hr'], bins=bins, labels=labels, right=False)
    usage_data = hour_df.groupby(['hour_bin', 'weekday'])['total_users'].sum().reset_index()
    
    plt.figure(figsize=(12, 6))
    for day in range(7):
        plt.plot(usage_data[usage_data['weekday'] == day]['hour_bin'],
                 usage_data[usage_data['weekday'] == day]['total_users'],
                 marker='o', label=f'Hari {day} (0=Senin, 6=Minggu)')
    plt.title('Penyewaan Sepeda Berdasarkan Jam dan Hari')
    plt.xlabel('Jam (Binned)')
    plt.ylabel('Total Penyewa Sepeda')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt.gcf())

def get_total_by_weekday(hour_df):
    return hour_df.groupby('weekday')['total_users'].sum().reset_index()

def get_total_by_hour(hour_df):
    return hour_df.groupby('hr')['total_users'].sum().reset_index()

hour_df = pd.read_csv("all_data.csv")

with st.sidebar:
    st.image("logo.png")

    min_date = pd.to_datetime(hour_df['dteday'].min())
    max_date = pd.to_datetime(hour_df['dteday'].max())
    start_date, end_date = st.date_input(
        label='Rentang Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    selected_hours = st.sidebar.slider('Pilih Rentang Jam', min_value=0, max_value=23, value=(0, 23))
    selected_days = st.sidebar.multiselect(
        'Pilih Hari', 
        options=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'], 
        default=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    )
    
    day_mapping = {'Senin': 0, 'Selasa': 1, 'Rabu': 2, 'Kamis': 3, 'Jumat': 4, 'Sabtu': 5, 'Minggu': 6}
    selected_days_num = [day_mapping[day] for day in selected_days]

    filtered_df = hour_df[
        (pd.to_datetime(hour_df['dteday']).between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
        (hour_df['hr'].between(selected_hours[0], selected_hours[1])) &
        (hour_df['weekday'].isin(selected_days_num))
    ]
st.header('🚲 Aini\'s Bicycle Rent 🚲')

avg_total_users = filtered_df['total_users'].mean() if not filtered_df.empty else hour_df['total_users'].mean()
st.subheader('Summary Statistik')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rata-rata Penyewa : ", value=f"{avg_total_users:.2f}")

total_by_weekday = get_total_by_weekday(filtered_df)  
total_by_hour = get_total_by_hour(filtered_df)        
total_by_hour_day = filtered_df.groupby(['hr', 'weekday'])['total_users'].sum().reset_index()

st.subheader('Grafik Penyewa Daily dan Hourly')

col1, col2 = st.columns(2)
with col1:
    st.write("Grafik Penyewa per Hari")
    plot_weekday_rentals(total_by_weekday)
with col2:
    st.write("Grafik Penyewa per Jam")
    plot_hourly_rentals(total_by_hour)

st.subheader('Analisis Trend Penyewa berdasarkan Jam & Hari')
plot_hour_day_trend(total_by_hour_day)

st.subheader('Hubungan Suhu dan Kelembapan dengan Jumlah Penyewa')
plot_temp_humidity_heatmap(filtered_df)

st.subheader('Clustering Penyewa saat Pagi, Siang, Sore, Malam')
plot_binned_hour_usage(filtered_df)

st.caption('Copyright (c) 2023 - Aini\'s Bicycle Rent')