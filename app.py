import streamlit as st
import pandas as pd
from property_scrape import scrape_properties  # Import the scrape function

# Create a button to start scraping
if st.button("Scrape Properties"):
    with st.spinner("Scraping data... Please wait!"):
        # Run the scraper function
        scrape_properties()

    # After scraping, load the CSV into Streamlit
    try:
        df = pd.read_csv('property_onion_listings.csv')
        st.success("Data scraped successfully!")
        
        # Display the dataframe
        st.dataframe(df)

        # Add a button to download the CSV file
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='property_onion_listings.csv',
            mime='text/csv'
        )
    except FileNotFoundError:
        st.error("CSV file not found. Please scrape first.")