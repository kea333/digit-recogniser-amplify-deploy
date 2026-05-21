"""
Shared image preprocessing: any source image → (1, 1, 28, 28) numpy array
matching MNIST-CNN format (28×28, white digit on black, normalised).

Key fixes vs previous version:
  - Removed GaussianBlur (was destroying thin strokes of 7 and 9)
  - Added padded bounding box crop (preserves digit geometry)
  - Output shape is (1, 1, 28, 28) for CNN — not (1, 784) for MLP
  - Applied MNIST channel normalisation (mean=0.1307, std=0.3081)
"""
import numpy as np
from PIL import Image, ImageOps

# MNIST normalisation constants (channel mean and std)
MNIST_MEAN = 0.1307
MNIST_STD  = 0.3081


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Takes a PIL Image (from canvas or file upload) and returns
    a (1, 1, 28, 28) float32 numpy array ready for ONNX CNN inference.
    """
    # 1. Convert to grayscale
    image = image.convert("L")

    # 2. Auto-invert: if border pixels are bright → white background → invert
    arr_check = np.array(image)
    border_mean = np.mean([
        arr_check[0, :].mean(),
        arr_check[-1, :].mean(),
        arr_check[:, 0].mean(),
        arr_check[:, -1].mean(),
    ])
    if border_mean > 128:
        image = ImageOps.invert(image)

    # 3. Crop to bounding box with padding (10% of max dim)
    #    Padding preserves spatial geometry — critical for 7 and 9
    bbox = image.getbbox()
    if bbox is None:
        return np.zeros((1, 1, 28, 28), dtype=np.float32)

    left, upper, right, lower = bbox
    w, h = right - left, lower - upper
    pad  = max(int(max(w, h) * 0.10), 2)    # at least 2px padding

    img_w, img_h = image.size
    left  = max(left  - pad, 0)
    upper = max(upper - pad, 0)
    right = min(right + pad, img_w)
    lower = min(lower + pad, img_h)
    image = image.crop((left, upper, right, lower))

    # 4. Make square (preserve aspect ratio)
    max_dim = max(image.size)
    square  = Image.new("L", (max_dim, max_dim), 0)
    offset  = ((max_dim - image.size[0]) // 2, (max_dim - image.size[1]) // 2)
    square.paste(image, offset)

    # 5. Resize to 20×20 (digit occupies centre 20px of MNIST 28×28)
    #    NOTE: No blur applied — thin strokes of 7 and 9 must be preserved
    square = square.resize((20, 20), Image.LANCZOS)

    # 6. Center in 28×28 black canvas (MNIST standard)
    final = Image.new("L", (28, 28), 0)
    final.paste(square, (4, 4))

    # 7. Normalise to [0,1] then apply MNIST channel normalisation
    pixel_array = np.array(final, dtype=np.float32) / 255.0
    pixel_array = (pixel_array - MNIST_MEAN) / MNIST_STD

    # 8. Reshape to (1, 1, 28, 28): batch=1, channels=1, H=28, W=28
    return pixel_array.reshape(1, 1, 28, 28)
