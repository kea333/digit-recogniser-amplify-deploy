"""
Shared image preprocessing: any source image → (1, 784) numpy array
matching MNIST format (28×28, white digit on black, values in [0,1]).
"""
import numpy as np
from PIL import Image, ImageOps, ImageFilter


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Takes a PIL Image (from canvas or file upload) and returns
    a (1, 784) numpy array ready for Scikit-Learn prediction.
    """
    # 1. Convert to grayscale
    image = image.convert("L")

    # 2. Auto-invert: if the border is bright, the background is white → invert
    arr_check = np.array(image)
    border_mean = np.mean([
        arr_check[0, :].mean(),
        arr_check[-1, :].mean(),
        arr_check[:, 0].mean(),
        arr_check[:, -1].mean(),
    ])
    if border_mean > 128:
        image = ImageOps.invert(image)

    # 3. Crop to bounding box of non-zero pixels
    bbox = image.getbbox()
    if bbox is None:
        return np.zeros((1, 784), dtype=np.float64)
    image = image.crop(bbox)

    # 4. Make square (preserve aspect ratio)
    max_dim = max(image.size)
    square = Image.new("L", (max_dim, max_dim), 0)
    offset = ((max_dim - image.size[0]) // 2, (max_dim - image.size[1]) // 2)
    square.paste(image, offset)

    # 5. Resize to 20×20 (digit area in MNIST is ~20×20)
    square = square.resize((20, 20), Image.LANCZOS)

    # 6. Slight Gaussian blur to smooth jagged edges
    square = square.filter(ImageFilter.GaussianBlur(radius=1))

    # 7. Center in 28×28 black canvas
    final = Image.new("L", (28, 28), 0)
    final.paste(square, (4, 4))

    # 8. Normalize and flatten
    pixel_array = np.array(final, dtype=np.float64) / 255.0
    return pixel_array.reshape(1, 784)
