import streamlit as st
import requests
from datetime import datetime
import pydeck as pdk
import pandas as pd
import folium
from streamlit_folium import st_folium


# --- CONFIG DE LA PAGE ---
st.set_page_config(
    page_title="TaxiFareModel",
    page_icon="🚕",
    layout="centered"
)

# --- TITRE AVEC "LOGO" EMOJI + TEXTE ---
col1, col2 = st.columns([1, 5])

with col1:
    st.markdown(
        "<div style='font-size:60px; line-height:60px;'>🚕</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<h1 style='color: #87CEEB; margin-top: 10px;'>TaxifareModel - Prediction</h1>",
        unsafe_allow_html=True
    )


st.markdown(
    "<h2 style='color: #FFA8A8;'>Parameters</h2>",
    unsafe_allow_html=True
)


# CSS + JS pour colorer les champs
st.markdown("""
<style>
.input-ok {
    border: 2px solid #4CAF50 !important; /* vert */
    border-radius: 5px;
}
.input-bad {
    border: 2px solid #FF6F6F !important; /* rouge pastel */
    border-radius: 5px;
}
</style>

<script>
function updateColor() {
    const targets = [
        "job-date",
        "job-hour",
        "pickup-long",
        "pickup-lat",
        "dropoff-long",
        "dropoff-lat",
        "passengers"
    ];

    targets.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        const input = el.querySelector("input");
        if (!input) return;

        if (input.value === "" || input.value === null) {
            input.classList.add("input-bad");
            input.classList.remove("input-ok");
        } else {
            input.classList.add("input-ok");
            input.classList.remove("input-bad");
        }
    });
}

setInterval(updateColor, 300);
</script>
""", unsafe_allow_html=True)

st.markdown('<div id="job-date">', unsafe_allow_html=True)
date = st.date_input("Job date", datetime.today())
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="job-hour">', unsafe_allow_html=True)
time = st.time_input("Job hour", datetime.now().time())
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="pickup-long">', unsafe_allow_html=True)
pickup_longitude = st.number_input("Pickup longitude", value=-73.985428)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="pickup-lat">', unsafe_allow_html=True)
pickup_latitude = st.number_input("Pickup latitude", value=40.748817)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="dropoff-long">', unsafe_allow_html=True)
dropoff_longitude = st.number_input("Dropoff longitude", value=-73.985428)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="dropoff-lat">', unsafe_allow_html=True)
dropoff_latitude = st.number_input("Dropoff latitude", value=40.748817)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div id="passengers">', unsafe_allow_html=True)
passenger_count = st.number_input("Passengers number", min_value=1, max_value=8, value=1)
st.markdown('</div>', unsafe_allow_html=True)

# Carte centrée sur New York

# --- Données ---
data = pd.DataFrame({
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude]
})

pickup_lat = pickup_latitude
pickup_lon = pickup_longitude

drop_lat = dropoff_latitude
drop_lon = dropoff_longitude

# --- Carte Folium ---
m = folium.Map(location=[pickup_lat, pickup_lon], zoom_start=12)

# --- Logo personnalisé pour le pickup ---
pickup_icon = folium.features.CustomIcon(
    "https://banner2.cleanpng.com/20180329/kdq/avijtsv9b.webp",   # ton logo
    icon_size=(50, 50)
)

folium.Marker(
    location=[pickup_lat, pickup_lon],
    icon=pickup_icon,
    tooltip="Point de départ"
).add_to(m)

# --- Marqueur normal pour le dropoff ---
folium.Marker(
    location=[drop_lat, drop_lon],
    tooltip="Destination"
).add_to(m)

# --- Affichage ---
st.title("🗽 NYC Taxi Ride Map")
st_folium(m, width=700, height=500)


url = "https://data-fast-api-988182740591.europe-west1.run.app/predict"

if st.button("Get prediction"):
    # Fusion date + time
    pickup_datetime = datetime.combine(date, time).isoformat()

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count
    }

    st.write("📤 Paramètres envoyés :", params)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Erreur si code != 200

        prediction = response.json().get("fare", None)

        if prediction is not None:
            st.success(f"💰 Prix estimé : **{prediction:.2f} $**")
        else:
            st.error("L'API n'a pas renvoyé de prédiction.")

    except Exception as e:
        st.error(f"Erreur lors de l'appel API : {e}")
