from PIL import Image
import numpy as np

def image_to_array(image_path, threshold=128, resize=None):
    """Load an image from file and convert it to a 0/1 numpy array.
    
    Args:
        image_path: Path to the image file (PNG, JPG, etc.)
        threshold: Pixel value threshold for binary conversion (0-255)
        resize: Optional tuple (width, height) to resize image before conversion
    
    Returns:
        numpy array of 0s and 1s
    """
    # Open the image
    img = Image.open(image_path)
    
    # Resize if requested
    if resize is not None:
        img = img.resize(resize)
    
    # Convert to grayscale if necessary
    if img.mode != 'L':
        img = img.convert('L')
    
    # Convert PIL Image to numpy array
    arr = np.array(img)
    
    # Convert to binary array (0s and 1s) based on threshold
    binary_arr = (arr > threshold).astype(int)
    
    return binary_arr


def image_to_array_4_values(image_path, thresholds=[64, 128, 192], resize=None):
    """Load an image from file and convert it to 0/1/2/3 numpy array based on thresholds.
    
    Args:
        image_path: Path to the image file (PNG, JPG, etc.)
        thresholds: List of 3 threshold values to create 4 levels (0-255)
                   Results: 0 if pixel <= thresholds[0]
                           1 if thresholds[0] < pixel <= thresholds[1]
                           2 if thresholds[1] < pixel <= thresholds[2]
                           3 if pixel > thresholds[2]
        resize: Optional tuple (width, height) to resize image before conversion
    
    Returns:
        numpy array of 0s, 1s, 2s, and 3s
    """
    # Open the image
    img = Image.open(image_path)
    
    # Resize if requested
    if resize is not None:
        img = img.resize(resize)
    
    # Convert to grayscale if necessary
    if img.mode != 'L':
        img = img.convert('L')
    
    # Convert PIL Image to numpy array
    arr = np.array(img)
    
    # Convert to 4-value array based on thresholds
    result = np.zeros_like(arr, dtype=int)
    result[arr > thresholds[0]] = 1
    result[arr > thresholds[1]] = 2
    result[arr > thresholds[2]] = 3
    
    return result


# Example usage
if __name__ == "__main__":
    # Example: Convert an image file to numpy array (binary 0/1)
    # mat = image_to_array("your_image.png")
    # print(f"Shape: {mat.shape}")
    
    # Example with resize parameter (binary 0/1)
    # mat = image_to_array("your_image.png", resize=(16, 16))
    # print(f"Shape: {mat.shape}")
    
    # Example with 4-value conversion (0/1/2/3)
    mat = image_to_array_4_values("images/drone.png", resize=(32, 32), thresholds=[125, 150, 250])
    print(f"Shape: {mat.shape}")
    print(f"Array:\n{mat.tolist()}")

    for row in mat:
        for char in row:
            if char == 0:
                print(' ', end='')
            elif char == 1:
                print('#', end='')
            elif char == 2:
                print('*', end='')
            elif char == 3:
                print('+', end='')
        print()
    
    mat = image_to_array("images/bitsculptlogonotext.png", resize=(32, 32))
    print(f"Shape: {mat.shape}")
    print(f"Array:\n{mat.tolist()}")

    for row in mat:
        for char in row:
            if char == 0:
                print(' ', end='')
            elif char == 1:
                print('#', end='')
        print()
    
    pass


