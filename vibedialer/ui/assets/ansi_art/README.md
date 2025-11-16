# ANSI Art Collection

This directory contains ANSI art that is randomly displayed on the welcome screen when launching VibeDialer.

## Requirements

### File Format
- **Extension**: `.txt` (plain text files) or `.ans` (ANSI art files with escape codes)
- **Encoding**: UTF-8
- **Naming**: Any filename ending in `.txt` or `.ans`/`.ANS` (e.g., `example_01.txt`, `my_art.ans`)

### Art Specifications

#### Size Recommendations
- **Width**: Maximum 80 characters per line (terminal standard)
- **Height**: 10-20 lines recommended for best display
- **Aspect Ratio**: Landscape orientation works best

#### Character Guidelines
- **Box Drawing Characters**: ╔ ═ ╗ ║ ╚ ╝ ┌ ─ ┐ │ └ ┘ (recommended)
- **ASCII Characters**: Standard ASCII (a-z, A-Z, 0-9, punctuation) work great
- **Unicode**: Full Unicode support, but test in terminal first
- **Avoid**: Control characters, ANSI escape codes (styling is handled by VibeDialer)

#### Styling

For `.txt` files (plain text):
- **Colors**: Applied automatically using vaporwave color scheme (cyan)
- **No embedded styling needed**: Don't include ANSI color codes
- **Plain text only**: The application handles all styling

For `.ans` files (ANSI art):
- **Embedded ANSI codes**: Include your own ANSI escape sequences for colors and formatting
- **Full color control**: Use standard ANSI escape codes (e.g., `\x1b[31m` for red)
- **Preserved formatting**: Your ANSI codes will be rendered as-is, preserving original styling

### Best Practices

1. **Test in a terminal**: View your art file with `cat filename.txt` to ensure it displays correctly
2. **Keep it simple**: Complex multi-color ANSI art should be converted to plain text first
3. **Use a monospace font**: Create art using a monospace editor or generator
4. **Check character width**: Some Unicode characters are wide (占 vs a) - test carefully
5. **Consider the audience**: Keep content appropriate for war dialing/security/retro computing themes

### Examples

```
Simple box:
╔═══════════════════════╗
║   Hello, Dialer!      ║
╚═══════════════════════╝

ASCII banner:
    __      _____ ____  ______
    \ \    / /_ _|  _ \|  ____|
     \ \  / / | || |_) | |__
      \ \/ /  | ||  _ <|  __|
       \  /  _| || |_) | |____
        \/  |___|____/|______|
```

### Adding Your Art

**For plain text art (.txt):**
1. Create a new `.txt` file in this directory
2. Add your ASCII art as plain text
3. The art will be styled automatically with vaporwave colors

**For ANSI art (.ans):**
1. Create a new `.ans` file in this directory
2. Include ANSI escape codes for your desired colors and formatting
3. The art will be rendered with your original styling preserved

Both formats are automatically included in the random rotation. No code changes needed!

### Tools for Creating ANSI Art

- **ASCII Art Generators**:
  - [patorjk.com/software/taag/](http://patorjk.com/software/taag/) - Text to ASCII
  - [asciiart.eu](https://www.asciiart.eu/) - Pre-made art collection

- **Drawing Tools**:
  - [moebius](https://github.com/blocktronics/moebius) - ANSI/ASCII art editor
  - [PabloDraw](http://picoe.ca/products/pablodraw/) - ANSI art editor

- **Text Editors**:
  - Any editor with a monospace font works fine for simple art

### Current Collection

The application will load all `.txt` and `.ans` files from this directory. Currently installed:
- `example_01.txt` - Placeholder welcome message

Feel free to add as many as you like - one will be randomly selected each time!

### ANSI Escape Code Reference

For `.ans` files, here are some common ANSI escape codes:

**Colors:**
- `\x1b[30m` - Black
- `\x1b[31m` - Red
- `\x1b[32m` - Green
- `\x1b[33m` - Yellow
- `\x1b[34m` - Blue
- `\x1b[35m` - Magenta
- `\x1b[36m` - Cyan
- `\x1b[37m` - White

**Formatting:**
- `\x1b[1m` - Bold
- `\x1b[2m` - Dim
- `\x1b[4m` - Underline
- `\x1b[0m` - Reset all formatting

**Example:**
```
\x1b[1;31m╔═══╗\x1b[0m
\x1b[1;32m║ H ║\x1b[0m
\x1b[1;34m╚═══╝\x1b[0m
```
