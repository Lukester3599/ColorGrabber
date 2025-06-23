import time
import sys
import pyautogui
import mss
import colorama

colorama.init()

CSI = "\x1b["

def set_fg_rgb(r, g, b):
    """Return ANSI sequence to set foreground color to (r,g,b)."""
    return f"{CSI}38;2;{r};{g};{b}m"

def set_bg_rgb(r, g, b):
    """Return ANSI sequence to set background color to (r,g,b)."""
    return f"{CSI}48;2;{r};{g};{b}m"

def reset_colors():
    """Return ANSI sequence to reset all colors."""
    return f"{CSI}0m"

def luminance(r, g, b):
    """
    Compute perceived luminance of an sRGB color.
    Formula reference: https://en.wikipedia.org/wiki/Relative_luminance
    """
    # Linearize each channel
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    R, G, B = lin(r), lin(g), lin(b)
    # coefficients per ITU-R BT.709
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def main():
    THRESHOLD = 0.2
    # If luminance < THRESHOLD, we treat the color as "dark"
    with mss.mss() as sct:
        print("Press Ctrl-C to quit")
        try:
            while True:
                x, y = pyautogui.position()
                monitor = {"left": x, "top": y, "width": 1, "height": 1}
                img = sct.grab(monitor)
                px = img.pixel(0, 0)

                # mss on Windows returns BGRA, other platforms BGR
                if len(px) == 4:
                    b, g, r, _ = px
                else:
                    r, g, b = px

                # compute luminance
                L = luminance(r, g, b)

                # Build ANSI sequences
                fg_seq = set_fg_rgb(r, g, b)
                if L < THRESHOLD:
                    # Background to white
                    bg_seq = set_bg_rgb(255, 255, 255)
                else:
                    # Reset background (i.e. leave terminal default)
                    bg_seq = ""

                hexv = f"#{r:02X}{g:02X}{b:02X}"
                out = (
                    f"{fg_seq}{bg_seq}@({x:4d},{y:4d}) "
                    f"HEX={hexv} RGB=({r},{g},{b})"
                    f"{reset_colors()}"
                )
                sys.stdout.write(out + "   \r")
                sys.stdout.flush()
                time.sleep(0.1)

        except KeyboardInterrupt:
            # On exit, clear any styling
            print()
            print(reset_colors(), "Exiting")

if __name__ == "__main__":
    main()
