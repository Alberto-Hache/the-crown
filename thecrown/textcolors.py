###############################################################
# IMPORT

# Standard library imports
import sys

# ANSI escape codes

ansi_esc_ini = '\u001b['

# Dictionaries for colors:

txt_fg = {
    'black':    30,
    'red':      31,
    'green':    32,
    'yellow':   33,
    'blue':     34,
    'magenta':  35,
    'cyan':     36,
    'white':    37,
    'reset':    0
}

txt_intensity = {
    'normal':   0,
    'bright':   60
}

txt_style = {
    'normal':   0,
    'bold':     1
}

bg_offset = 10

txt_reset = '0'

ansi_esc_end = 'm'


def colorize(text, color, intensity):
    """
    Add color and intensity to some text.

    Input:
        text:       string - some input text.
        color:      string - a value among:
                    'black', 'red', 'green', 'yellow', 'blue',
                    'magenta', 'cyan', 'white', 'reset'
        intensity:  string - a value among:
                    'normal', 'bright'

    Output:         string - the colorized text.

    """
    return (ansi_esc_ini + str(txt_fg[color]+txt_intensity[intensity]) +
            ansi_esc_end +
            text +
            ansi_esc_ini + txt_reset +
            ansi_esc_end + "")


def colorize_bg(text, fg_color, fg_intensity='normal',
                bg_color='reset', bg_intensity='normal',
                style='normal'):

    # Build basic fg & bg prefix.
    txt_str = ansi_esc_ini + \
            str(txt_fg[fg_color] +
                txt_intensity[fg_intensity]) + \
            ansi_esc_end + \
            ansi_esc_ini + \
            str(txt_fg[bg_color] +
                txt_intensity[bg_intensity] +
                bg_offset) + \
            ansi_esc_end
    # Build style part.
    if (style == 'bold'):
        style_str = ansi_esc_ini + str(txt_style[style]) + ansi_esc_end
    else:
        style_str = ""
    # Build end_str
    end_str = ansi_esc_ini + txt_reset + ansi_esc_end + ""

    return (txt_str + style_str + text + end_str)


def test_16_colors():
    print("Test of 16 colors:")
    for c in txt_fg:
        for i in txt_intensity:
            print(colorize("COLOR: "+i+' '+c, c, i))


def test_16_colors_bg():
    print("Test of 16 colors with BG:")
    for bg in txt_fg:
        for bg_i in txt_intensity:
            for c in txt_fg:
                for i in txt_intensity:
                    print(
                        colorize_bg(
                            "BG: " + bg_i+' '+bg + ", COLOR: "+i+' '+c,
                            c, i, bg, bg_i
                        )
                    )


if __name__ == '__main__':
    if len(sys.argv) == 1:
        test_16_colors()
    elif sys.argv[1] == 'bg':
        test_16_colors_bg()
    else:
        print(
            sys.argv[0] +
            ": Arguments are: (none) for 16 colors, 'bg' for background tests."
        )
