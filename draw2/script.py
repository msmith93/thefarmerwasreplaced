from PIL import Image, ImageDraw, ImageFont
import numpy as np

def letter_to_array_centered(letter, image_size=(32,32), font_path=None, font_size=28):
    """Return a 0/1 numpy array of a centered letter.
    This accounts for font glyph offsets (x0,y0) so letters are truly centered.
    """
    W, H = image_size
    img = Image.new('L', image_size, 0)
    draw = ImageDraw.Draw(img)

    # load a TrueType font if provided, else fallback to default
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("FreeMonoBold.ttf", font_size)
    except Exception:
        print("Oh no!")
        sys.exit(1)
        font = ImageFont.load_default()

    # Try to get precise glyph bbox (font.getbbox preferred)
    try:
        # font.getbbox returns (x0, y0, x1, y1)
        x0, y0, x1, y1 = font.getbbox(letter)
        glyph_w, glyph_h = x1 - x0, y1 - y0
        # To center: compute top-left so that glyph is centered, and compensate for x0,y0
        pos_x = (W - glyph_w) // 2 - x0
        pos_y = (H - glyph_h) // 2 - y0

    except AttributeError:
        # Older Pillow: use draw.textbbox if available (ImageDraw >= 8.x)
        try:
            bbox = draw.textbbox((0,0), letter, font=font)
            x0, y0, x1, y1 = bbox
            glyph_w, glyph_h = x1 - x0, y1 - y0
            pos_x = (W - glyph_w) // 2 - x0
            pos_y = (H - glyph_h) // 2 - y0
        except AttributeError:
            # Fallback very old: approximate with textsize (less accurate for some fonts)
            glyph_w, glyph_h = draw.textsize(letter, font=font)
            pos_x = (W - glyph_w) // 2
            pos_y = (H - glyph_h) // 2

    # Draw the letter
    draw.text((pos_x, pos_y), letter, fill=255, font=font)

    arr = np.array(img)
    return (arr > 128).astype(int)


# Example usage
if __name__ == "__main__":

    IMAGE_SIZE = (16,16)
    FONT_SIZE = 20
    LETTERS = ['S', 'U', 'B', 'C', 'R', 'I', 'E']
    for letter in LETTERS:
        mat = letter_to_array_centered(letter, image_size=IMAGE_SIZE, font_size=FONT_SIZE)
        print(f"{letter}_pixels = {mat.tolist()}")

       #for row in mat:
       #     print(''.join('#' if v else ' ' for v in row))
    
