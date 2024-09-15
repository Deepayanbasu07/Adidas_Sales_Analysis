import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Set wide layout and page title
st.set_page_config(layout="wide", page_title="Adidas Sales Dashboard")

# Load the data
df = pd.read_excel("Adidas.xlsx")

# Custom CSS for layout and branding
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #F5F5F5;
    }
    .sidebar .sidebar-content {
        background-color: #FF6F00;
    }
    .sidebar .sidebar-content .sidebar-item {
        color: #FFFFFF;
    }
    .sidebar .sidebar-content .sidebar-item:hover {
        background-color: #FF8C00;
    }
    .css-1d391kg {
        background-color: #FF6F00;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- Image Loading ---
# Load the renamed branding images here
header_logo = Image.open('images/adidas-neon-logo-3840x2160-17571.jpeg')
sidebar_logo1 = Image.open('images/adidas-leaves-logo-wallpaper-preview.jpg')
sidebar_logo2 = Image.open('images/adidas-leaves-logo-wallpaper-preview.jpg')
divider_image = Image.open('images/HD-wallpaper-adidas-global-brand-advertising.jpg')

# --- Sidebar Branding ---
# Sidebar with multiple branding images
st.sidebar.image(sidebar_logo1, width=150)  # Primary sidebar logo at the top
st.sidebar.title("Adidas Sales Dashboard")
st.sidebar.markdown("Explore Adidas sales data through interactive visualizations.")

# Date filter in the sidebar
start_date = st.sidebar.date_input("Start Date", datetime.date(2021, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2023, 1, 1))

# Filter data based on date
df = df[(df["InvoiceDate"] >= pd.to_datetime(start_date)) & (df["InvoiceDate"] <= pd.to_datetime(end_date))]

# --- Main Header Section ---
# Header logo and title
st.image(header_logo, use_column_width=True)  # Header logo image at the top
st.markdown(
    f"""
    <div style='display:flex; align-items:center;'>
        <h1 style='font-size:64px;'>Adidas Interactive Sales Dashboard</h1>
    </div>
    """, unsafe_allow_html=True
)
st.write(f"**Last Updated**: {datetime.datetime.now().strftime('%d %B %Y')}")

# Custom Metrics
total_sales = df['TotalSales'].sum()
average_profit = df['OperatingProfit'].mean()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
with col2:
    st.metric(label="Average Operating Profit", value=f"${average_profit:,.2f}")

# --- Divider Image Between Sections ---
st.image(divider_image, width=1200)  # Divider image between sections for improved visual flow

# --- Sales by Retailer and Date ---
st.markdown("### Total Sales by Retailer and Over Time")
col1, col2 = st.columns([0.5, 0.5])

# Sales by Retailer
with col1:
    retailer_sales_fig = px.bar(df, x="Retailer", y="TotalSales", title="Total Sales by Retailer",
                                labels={"TotalSales": "Total Sales ($)"}, template="seaborn")
    st.plotly_chart(retailer_sales_fig, use_container_width=True)

# Sales Trend Over Time
df["Month_Year"] = df["InvoiceDate"].dt.strftime("%b'%y")
sales_over_time = df.groupby("Month_Year")["TotalSales"].sum().reset_index()
with col2:
    time_sales_fig = px.line(sales_over_time, x="Month_Year", y="TotalSales", title="Total Sales Over Time",
                             labels={"TotalSales": "Total Sales ($)"}, template="seaborn")
    st.plotly_chart(time_sales_fig, use_container_width=True)

# Sidebar download option
st.sidebar.markdown("#### Download Data")
data_choice = st.sidebar.radio("Choose data to download:", ["Retailer Sales", "Monthly Sales"])
if data_choice == "Retailer Sales":
    st.sidebar.download_button("Download Retailer Sales Data", df[["Retailer", "TotalSales"]].to_csv(),
                               "RetailerSales.csv", mime="text/csv")
elif data_choice == "Monthly Sales":
    st.sidebar.download_button("Download Monthly Sales Data", sales_over_time.to_csv(),
                               "MonthlySales.csv", mime="text/csv")

# --- Sales and Units Sold by State ---
st.markdown("### Sales and Units Sold by State")
state_sales_units = df.groupby("State")[["TotalSales", "UnitsSold"]].sum().reset_index()

state_fig = go.Figure()
state_fig.add_trace(go.Bar(x=state_sales_units["State"], y=state_sales_units["TotalSales"], name="Total Sales"))
state_fig.add_trace(go.Scatter(x=state_sales_units["State"], y=state_sales_units["UnitsSold"], mode="lines+markers",
                               name="Units Sold", yaxis="y2"))

state_fig.update_layout(
    title="Total Sales and Units Sold by State",
    xaxis=dict(title="State"),
    yaxis=dict(title="Total Sales", showgrid=False),
    yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
    template="seaborn"
)
st.plotly_chart(state_fig, use_container_width=True)

# --- Treemap: Total Sales by Region and City ---
st.markdown("### Total Sales by Region and City (Treemap)")
treemap_data = df.groupby(["Region", "City"])["TotalSales"].sum().reset_index()
treemap_fig = px.treemap(treemap_data, path=["Region", "City"], values="TotalSales",
                         color="City", title="Sales by Region and City",
                         hover_data=["TotalSales"], template="seaborn")
st.plotly_chart(treemap_fig, use_container_width=True)

# --- Additional Features ---

# Total Sales by Region
st.markdown("### Total Sales by Region")
region_sales = df.groupby('Region')['TotalSales'].sum().reset_index()
region_sales_fig = px.bar(region_sales, x='Region', y='TotalSales',
                          labels={'TotalSales': 'Total Sales ($)'})
st.plotly_chart(region_sales_fig, use_container_width=True)

# Sales Trend Over Time (Monthly)
st.markdown("### Sales Trend Over Time (Monthly)")
df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
sales_trend = df.groupby('InvoiceMonth')['TotalSales'].sum().reset_index()
sales_trend_fig = go.Figure()
sales_trend_fig.add_trace(go.Scatter(x=sales_trend['InvoiceMonth'].astype(str), y=sales_trend['TotalSales'],
                                     mode='lines', name='Sales Trend'))
sales_trend_fig.update_layout(xaxis_title='Month', yaxis_title='Total Sales ($)')
st.plotly_chart(sales_trend_fig, use_container_width=True)

# Top 10 Products by Sales
st.markdown("### Top 5 Products by Sales")
top_products = df.groupby('Product')['TotalSales'].sum().sort_values(ascending=False).head(5).reset_index()
top_products_fig = px.bar(top_products, x='Product', y='TotalSales', 
                          labels={'TotalSales': 'Total Sales ($)'})
st.plotly_chart(top_products_fig, use_container_width=True)

# Sales Method Distribution (Pie Chart)
st.markdown("### Sales Method Distribution")
sales_method = df.groupby('SalesMethod')['TotalSales'].sum().reset_index()
sales_method_fig = px.pie(sales_method, names='SalesMethod', values='TotalSales', 
                          height=700, width=900)  # Adjusted size for larger chart
st.plotly_chart(sales_method_fig, use_container_width=False)

# Operating Profit by Region
st.markdown("### Operating Profit by Region")
region_profit = df.groupby('Region')['OperatingProfit'].sum().reset_index()
region_profit_fig = px.bar(region_profit, x='Region', y='OperatingProfit', 
                           labels={'OperatingProfit': 'Operating Profit ($)'})
st.plotly_chart(region_profit_fig, use_container_width=True)

# Heatmap of Sales by Product and Region
st.markdown("### Heatmap of Sales by Product and Region")
sales_heatmap = df.groupby(['Product', 'Region'])['TotalSales'].sum().reset_index()
sales_heatmap_pivot = sales_heatmap.pivot(index='Product', columns='Region', values='TotalSales')
sales_heatmap_fig = px.imshow(sales_heatmap_pivot,
                              color_continuous_scale=px.colors.sequential.Plasma,
                              labels={'color':'Total Sales ($)'} )
sales_heatmap_fig.update_layout(
    height=900,  # Adjust height as needed
    width=1400    # Adjust width as needed
)
st.plotly_chart(sales_heatmap_fig, use_container_width=True)


# Profitability by Product (Scatter Plot)
st.markdown("### Profitability by Product")
product_profit = df.groupby('Product').agg({'TotalSales': 'sum', 'OperatingProfit': 'sum'}).reset_index()
product_profit_fig = px.scatter(product_profit, x='TotalSales', y='OperatingProfit', size='OperatingProfit',
                                color='Product',
                                labels={'TotalSales': 'Total Sales ($)', 'OperatingProfit': 'Operating Profit ($)'})
st.plotly_chart(product_profit_fig, use_container_width=True)

# Additional KPIs Section
st.markdown("### Key Performance Indicators")

# Total Units Sold
total_units_sold = df['UnitsSold'].sum()

# Average Price per Unit
avg_price_per_unit = df['PriceperUnit'].mean()

# Gross Profit (Assuming CostPerUnit is estimated at 70% of PriceperUnit)
df['CostPerUnit'] = df['PriceperUnit'] * 0.7
df['GrossProfit'] = df['TotalSales'] - (df['UnitsSold'] * df['CostPerUnit'])
total_gross_profit = df['GrossProfit'].sum()

# Profit Margin (Operating Profit / Total Sales)
df['ProfitMargin'] = (df['OperatingProfit'] / df['TotalSales']) * 100
avg_profit_margin = df['ProfitMargin'].mean()

# Display these KPIs in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Units Sold", value=f"{total_units_sold:,}")
with col2:
    st.metric(label="Average Price per Unit", value=f"${avg_price_per_unit:,.2f}")
with col3:
    st.metric(label="Total Gross Profit", value=f"${total_gross_profit:,.2f}")
with col4:
    st.metric(label="Average Profit Margin", value=f"{avg_profit_margin:.2f}%")
    
st.markdown("### Cumulative Sales Over Time")
# Cumulative Sales Over Time
df['CumulativeSales'] = df['TotalSales'].cumsum()

# Plot Cumulative Sales
cumulative_sales_fig = px.line(df, x='InvoiceDate', y='CumulativeSales', title='Cumulative Sales Over Time',
                               labels={'CumulativeSales': 'Cumulative Sales ($)'}, template="seaborn")
st.plotly_chart(cumulative_sales_fig, use_container_width=True)


st.markdown("### Product-wise Sales Trend")
# Product-wise Sales Trend Over Time
product_sales_trend = df.groupby(['Product', 'InvoiceDate'])['TotalSales'].sum().reset_index()

# Plot Product-wise Sales Trend
product_sales_fig = px.line(product_sales_trend, x='InvoiceDate', y='TotalSales', color='Product',
                            title='Product-wise Sales Trend Over Time',
                            labels={'TotalSales': 'Total Sales ($)'}, template="seaborn")
st.plotly_chart(product_sales_fig, use_container_width=True)



# st.markdown("### Customer Segmentation by Retailer")
# # Sales per Retailer ID
# retailer_sales = df.groupby('RetailerID')['TotalSales'].sum().reset_index()

# # Plot Retailer Sales Distribution
# retailer_sales_fig = px.bar(retailer_sales, x='RetailerID', y='TotalSales', title='Sales by Retailer ID',
#                             labels={'TotalSales': 'Total Sales ($)'}, template="seaborn")
# st.plotly_chart(retailer_sales_fig, use_container_width=True)



st.markdown("### Correlation Heatmap")
# Correlation Heatmap
correlation_matrix = df[['TotalSales', 'OperatingProfit', 'PriceperUnit', 'UnitsSold', 'ProfitMargin']].corr()

# Plot Correlation Heatmap
heatmap_fig = px.imshow(correlation_matrix, text_auto=True, title='Correlation Heatmap',
                        labels={'color': 'Correlation Coefficient'})
heatmap_fig.update_layout(
    height=900,  # Adjust height as needed
    width=1400    # Adjust width as needed
)
st.plotly_chart(heatmap_fig, use_container_width=True)


st.markdown("### Box Plot for Operating Margin")
# Box Plot for Operating Margin
margin_boxplot_fig = px.box(df, x='Region', y='ProfitMargin', title='Operating Margin by Region',
                            labels={'ProfitMargin': 'Operating Margin (%)'}, template="seaborn")
st.plotly_chart(margin_boxplot_fig, use_container_width=True)



st.markdown("### Feature Engineering - Seasonality Features")
# Extracting Month, Quarter, and Day of the Week
df['Month'] = df['InvoiceDate'].dt.month
df['Quarter'] = df['InvoiceDate'].dt.quarter
df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek

# Visualization: Sales by Month
month_sales = df.groupby('Month')['TotalSales'].sum().reset_index()

month_sales_fig = px.bar(month_sales, x='Month', y='TotalSales', title='Total Sales by Month',
                         labels={'TotalSales': 'Total Sales ($)'}, template="seaborn")
st.plotly_chart(month_sales_fig, use_container_width=True)


st.markdown("### Profitability by Product (with Scatter Plot)")
# Profitability by Product (Scatter Plot)
product_profit = df.groupby('Product').agg({'TotalSales': 'sum', 'OperatingProfit': 'sum'}).reset_index()

product_profit_fig = px.scatter(product_profit, x='TotalSales', y='OperatingProfit', size='OperatingProfit',
                                color='Product', hover_name='Product',
                                labels={'TotalSales': 'Total Sales ($)', 'OperatingProfit': 'Operating Profit ($)'},
                                title='Profitability by Product')
st.plotly_chart(product_profit_fig, use_container_width=True)




# --- Footer Branding ---
# Footer logo and tagline
st.markdown("### Powered by Adidas Sales Data Analysis")

# Create four columns for the four images
col1, col2, col3, col4 = st.columns(4)

# Load the footer images (replace with your actual image paths)
footer_image1 = Image.open('images/f1.jpg').resize((300, 200))
footer_image2 = Image.open('images/f2.jpg').resize((300, 200))
footer_image3 = Image.open('images/f3.jpg').resize((300, 200))
footer_image4 = Image.open('images/adidas-brand-campaigns-1.jpg').resize((300, 200))

# Display the images in the respective columns
with col1:
    st.image(footer_image1, use_column_width=True)
with col2:
    st.image(footer_image2, use_column_width=True)
with col3:
    st.image(footer_image3, use_column_width=True)
with col4:
    st.image(footer_image4, use_column_width=True)

# Add personalized text and contact details after images
st.markdown(f"**Last Updated on {datetime.datetime.now().strftime('%d %B %Y')}**")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>Hi, I am Deepayan Basu from IIT Jodhpur. I am an aspiring Data Analyst/Scientist.</p>
        <p>Thank you for exploring the Adidas Sales Dashboard.</p>
        <p>Contact me: <a href='mailto:deepayanbasu5@gmail.com'>deepayanbasu5@gmail.com</a></p>
        <p>Connect on LinkedIn: <a href='www.linkedin.com/in/deepayan-basu-06a5b123b'>LinkedIn Profile</a></p>
    </div>
    """, unsafe_allow_html=True
)
