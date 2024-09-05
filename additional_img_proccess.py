import rasterio
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt

# Load the SWIR composite TIFF file
with rasterio.open("swir_composite.tiff") as dataset:
    # Read the bands (B12, B8A, B04) from the dataset
    band12 = dataset.read(1)  # SWIR band B12
    band8A = dataset.read(2)  # NIR band B8A
    band04 = dataset.read(3)  # Red band B04

    # Normalize the bands (optional, helps with displaying the image)
    def normalize(array):
        array_min, array_max = array.min(), array.max()
        return ((array - array_min) / (array_max - array_min))

    band12_norm = normalize(band12)
    band8A_norm = normalize(band8A)
    band04_norm = normalize(band04)

    # Stack bands to form RGB image (R = B12, G = B8A, B = B04)
    swir_rgb = np.dstack((band12_norm, band8A_norm, band04_norm))

    # Plot the image using matplotlib
    plt.imshow(swir_rgb)
    plt.title("SWIR Composite RGB")
    plt.axis("off")
    plt.savefig("swir_composite_result.png", dpi=300, bbox_inches='tight')
    plt.show()
