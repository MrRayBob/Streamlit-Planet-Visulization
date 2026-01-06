import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image

st.title("Interactive 3D Jupiter Globe")

# Load the Jupiter texture
texture_file = "2k_jupiter.jpg"
try:
    img = Image.open(texture_file)
    img_array = np.array(img)
    has_texture = True
except Exception as e:
    st.warning(f"Could not load texture: {e}. Make sure {texture_file} is in the same directory as app.py")
    has_texture = False

# Create a sphere mesh with higher resolution for better texture mapping
resolution = 100
u = np.linspace(0, 2 * np.pi, resolution)
v = np.linspace(0, np.pi, resolution)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))

# Create the figure
fig = go.Figure()

if has_texture:
    # Resize texture to match sphere resolution
    img_resized = img.resize((resolution, resolution))
    img_array_resized = np.array(img_resized)
    
    # Flip vertically to match sphere orientation
    img_array_resized = np.flipud(img_array_resized)
    
    # Calculate brightness value for each pixel (used to map colors)
    surfacecolor = np.mean(img_array_resized, axis=2)
    
    # Build colorscale by sampling colors from entire image
    # Sort pixels by brightness and sample evenly to capture all color variations
    pixels = img_array_resized.reshape(-1, 3)
    brightness = surfacecolor.flatten()
    sorted_indices = np.argsort(brightness)
    
    # Sample 256 colors evenly across brightness range
    n_colors = 256
    sample_indices = np.linspace(0, len(sorted_indices)-1, n_colors).astype(int)
    colorscale = []
    for i, idx in enumerate(sample_indices):
        rgb = pixels[sorted_indices[idx]]
        colorscale.append([i/(n_colors-1), f'rgb({rgb[0]},{rgb[1]},{rgb[2]})'])
    
    # Add sphere with custom colorscale and lighting
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        surfacecolor=surfacecolor,
        colorscale=colorscale,
        showscale=False,
        hoverinfo='skip',
        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.1, roughness=0.9)
    ))
else:
    # Fallback to orange sphere
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, 'rgb(255, 140, 0)'], [1, 'rgb(255, 165, 0)']],
        showscale=False,
        hoverinfo='skip'
    ))

# Update layout for better appearance
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor='black',
        aspectmode='data',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    width=700,
    height=700,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='black'
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.write("You can interact with the globe by clicking and dragging to rotate, and scrolling to zoom.")
