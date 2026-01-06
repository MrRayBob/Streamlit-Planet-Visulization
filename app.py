import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image

st.title("Interactive 3D Globe")

# Planet Selector in the sidebar
planet = st.sidebar.selectbox(
    "Planet Selector",
    ("Earth", "Jupiter", "Mars")
)
# Resolution Selector in the sidebar
resolution = st.sidebar.selectbox(
    "Resolution Selector",
    (256, 512, 1024, 2048), index=0, 
    help="Higher resolution will provide a smoother globe but may take longer to load."
)

# Load the Jupiter texture
match (planet):
    case "Earth":
        texture_file = "2k_earth.jpg"
    case "Jupiter":
        texture_file = "2k_jupiter.jpg"
    case "Mars":
        texture_file = "2k_mars.jpg"
    case _:
        texture_file = "2k_earth.jpg" # default to Earth if invalid selection
try:
    img = Image.open(texture_file).convert("RGB").transpose(Image.Transpose.ROTATE_270).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    img_array = np.array(img)
    has_texture = True
except Exception as e:
    st.warning(f"Could not load texture: {e}. Make sure {texture_file} is in the same directory as app.py")
    has_texture = False

def build_sphere_mesh(resolution: int):
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    uu, vv = np.meshgrid(u, v, indexing="ij")
    x = np.cos(uu) * np.sin(vv)
    y = np.sin(uu) * np.sin(vv)
    z = np.cos(vv)
    return u, v, x, y, z

# Create the figure
fig = go.Figure()

if has_texture:
    height, width, _ = img_array.shape
    resolution = min(resolution, min(height, width))
    u, v, x, y, z = build_sphere_mesh(resolution)

    u_idx = (np.linspace(0, width - 1, resolution)).astype(int)
    v_idx = (np.linspace(0, height - 1, resolution)).astype(int)
    texture = img_array[np.ix_(v_idx, u_idx)]

    colors = texture.reshape(-1, 3)
    vertex_colors = [f"rgb({r},{g},{b})" for r, g, b in colors]

    res_v = resolution
    faces_i = []
    faces_j = []
    faces_k = []
    for i in range(resolution - 1):
        for j in range(res_v - 1):
            v0 = i * res_v + j
            v1 = v0 + 1
            v2 = v0 + res_v
            v3 = v2 + 1
            faces_i.extend([v0, v1])
            faces_j.extend([v2, v2])
            faces_k.extend([v1, v3])

    fig.add_trace(go.Mesh3d(
        x=x.reshape(-1),
        y=y.reshape(-1),
        z=z.reshape(-1),
        i=faces_i,
        j=faces_j,
        k=faces_k,
        vertexcolor=vertex_colors,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.8, specular=0.2, roughness=0.9),
        hoverinfo="skip"
    ))
else:
    # Fallback to orange sphere
    resolution = 100
    _, _, x, y, z = build_sphere_mesh(resolution)
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
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
    ),
    width=700,
    height=700,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='black'
)

st.plotly_chart(fig, width='stretch') # Display Planet

