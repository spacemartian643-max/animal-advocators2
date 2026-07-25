import streamlit as st

st.set_page_config(page_title="Animal Advocators")

# This shows the title of the website.
st.title("Animal Advocators")

# This lets users search for an animal or location.
search = st.text_input("Search")

# This lets users choose a donation amount.
st.header("Donate")
amount = st.slider("Donation amount ($)",0,500,25)
if st.button("Donate"):
    st.success(f"Thank you for donating ${amount}!")

# This lets users pick a location on a simple map.
st.header("Choose a Location")
st.map({"lat":[37.7749],"lon":[-122.4194]})
lat=st.number_input("Latitude",value=37.7749)
lon=st.number_input("Longitude",value=-122.4194)
st.write("Selected location:",lat,lon)
