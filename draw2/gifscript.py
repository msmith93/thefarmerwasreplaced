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
                    [1 if frame.getpixel((x, y)) < threshold else 0 for x in range(size[0])]
                    for y in range(size[1])
                ]
                frames.append(mat)
                im.seek(im.tell() + 1)
        except EOFError:
            pass
    return frames


# Example usage
if __name__ == "__main__":
    frames = gif_to_arrays("images/coolgif.gif", size=(32, 32), threshold=128)

    frame_pixels = []
    for frame in frames:
        nums = []
        for bitlist in frame:

            num = 0
            for bit in bitlist:
                num = (num << 1) | bit

            nums += [num]
        # print(nums)
        frame_pixels += [nums]
    
    print(frame_pixels)
