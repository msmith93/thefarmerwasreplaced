from PIL import Image
import numpy as np
import json

def gif_to_arrays(path, size=(32, 32), threshold=128):
    """Convert all frames in a GIF to 2D 0/1 arrays."""
    frames = []
    with Image.open(path) as im:
        try:
            while True:
                # Convert to grayscale and resize
                frame = im.convert("L").resize(size)
                # Convert to binary 0/1
                mat = [
                    [0 if frame.getpixel((x, y)) < threshold else 1 for x in range(size[0])]
                    for y in range(size[1])
                ]
                frames.append(mat)
                im.seek(im.tell() + 1)
        except EOFError:
            pass
    return frames


# Example usage
if __name__ == "__main__":
    frames = gif_to_arrays("images/yinyangspin.gif", size=(32, 32), threshold=128)

    frame_pixels = []
    for frame in frames:
        nums = []
        for rowpixels in frame:

            num = 0
            for pixel in rowpixels:
                num = (num << 1) | pixel

            nums += [num]
        # print(nums)
        frame_pixels += [nums]
    
    print(frame_pixels)

    # Visualize
    # for frame in frames:
    #     for row in frame:
    #         for char in row:
    #             if char == 0:
    #                 print(' ', end='')
    #             elif char == 1:
    #                 print('#', end='')
    #         print()
