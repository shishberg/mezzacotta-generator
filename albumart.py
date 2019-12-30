from getflickr import FlickrGettr
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import glob
import mispell
import cv2
import numpy


class AlbumArt():
    def __init__(self, band_name, album_title, keywords):
        self.band_name = band_name
        self.album_title = album_title
        self.keywords = keywords

        self.fg = FlickrGettr()

        # Create canvas for album pic
        self.inverted_colours = random.random() < 0.4

        if self.inverted_colours:
            bg_colour = [255, random.randrange(192, 256), random.randrange(128, 256)]
        else:
            bg_colour = [0, random.randrange(64), random.randrange(128)]
        random.shuffle(bg_colour)
        self.cover = Image.new("RGB", (800,800), tuple(bg_colour))

    def drawBand(self, typeface, colour):
        # Draw the band name, trying smaller font sizes if needed
        d = ImageDraw.Draw(self.cover)
        band_font_size = random.randrange(80, 160)

        done = False
        while not done:
            band_font = ImageFont.truetype(typeface, band_font_size)
            text_width, text_height = d.textsize(self.band_name, band_font)
            if text_width > 760:
                band_font_size -= 4
            else:
                done = True

        if '\n' in self.band_name:
            d.multiline_text((20, 20), self.band_name, font=band_font, fill=colour,
                             spacing=int(band_font_size * 0.2))
        else:
            d.multiline_text((400 - (text_width / 2), 20), self.band_name, font=band_font, fill=colour,
                             spacing=int(band_font_size * 0.2))

    def drawTitle(self, typeface, colour):
        # Draw the album name
        d = ImageDraw.Draw(self.cover)
        done = False
        album_font_size = 56

        while not done:
            album_font = ImageFont.truetype(typeface, album_font_size)
            text_width, text_height = d.textsize(self.album_title, album_font)
            if text_width > 760:
                album_font_size -= 4
            else:
                done = True

        text_width, _ = d.textsize(self.album_title, font=album_font)
        d.text((780 - text_width, 720), self.album_title, font=album_font, fill=colour)

    def filter(self, command, full=False):

        if full:
            x_min, x_max, y_min, y_max = 0, 800, 0, 800
            width = 800
            height = 800
        else:
            # Cut out a random rectangle of the cover art, apply filter, then paste back.
            width = random.randrange(3, 7) * 100
            height = random.randrange(3, 7) * 100
            x_min = random.randrange(800 - width)
            x_max = x_min + width
            y_min = random.randrange(800 - height)
            y_max = y_min + height

        copy = self.cover.copy()
        cropped = copy.crop((x_min, y_min, x_max, y_max))

        if command == 'blur':
            cropped = cropped.filter(ImageFilter.GaussianBlur(random.random() * 2.0))

        if command == 'convolve':
            kernel_weights = [random.gauss(0, 3) for _ in range(9)]
            cropped = cropped.filter(ImageFilter.Kernel((3,3), kernel_weights))

        if command == 'quantize':
            cropped = cropped.quantize(random.randrange(2, 20), 2)

        if command == 'invert':
            cropped = ImageOps.invert(cropped)

        if command == 'grayscale':
            cropped = ImageOps.grayscale(cropped)

        if command == 'posterize':
            cropped = ImageOps.posterize(cropped, 1)

        if command == 'solarize':
            cropped = ImageOps.solarize(cropped, threshold=random.randrange(30, 230))

        if command == 'brightness':
            enhancer = ImageEnhance.Brightness(cropped)
            cropped = enhancer.enhance(0.25 + random.random() * 2.0)

        if command == 'edges':
            cropped = cropped.filter(ImageFilter.EDGE_ENHANCE_MORE)

        if command == 'canny':
            opencv_image = cv2.cvtColor(numpy.array(cropped), cv2.COLOR_RGB2BGR)
            cropped = Image.fromarray(cv2.cvtColor(cv2.Canny(opencv_image, 100, 200), cv2.COLOR_BGR2RGB))
            if self.inverted_colours:
                cropped = ImageOps.invert(cropped)

        if command == 'shuffle':
            # Copy/paste each 100x100 region into a random grid slot in a temporary image
            shuffle_idx = list(range((width // 100) * (height // 100)))
            random.shuffle(shuffle_idx)

            dest_imag = Image.new("RGB", (width, height))
            idx = 0
            for y_pos in range(0, height, 100):
                for x_pos in range(0, width, 100):
                    square = cropped.crop((x_pos, y_pos, x_pos + 100, y_pos + 100))

                    dest_idx = shuffle_idx[idx]

                    column = dest_idx % (width // 100)
                    row = dest_idx // (width // 100)

                    dest_imag.paste(square, (column * 100, row * 100))

                    idx += 1

            cropped = dest_imag

        if command == 'jitter':
            # Copy each 100x100 region into a slightly modified position in a temporary image

            dest_imag = cropped.copy()

            source_locations = []
            for y_pos in range(0, height, 100):
                for x_pos in range(0, width, 100):
                    source_locations.append((x_pos, y_pos))
            random.shuffle(source_locations)

            for x_pos, y_pos in source_locations:
                square = cropped.crop((x_pos, y_pos, x_pos + 100, y_pos + 100))

                dest_imag.paste(square, (x_pos + random.choice([-10,10]), y_pos + random.choice([-10, 10])))

            cropped = dest_imag


        if command == 'spin':
            # Rotate each 100x100 region to a random orientation
            dest_imag = Image.new("RGB", (width, height))
            for y_pos in range(0, height, 100):
                for x_pos in range(0, width, 100):
                    square = cropped.crop((x_pos, y_pos, x_pos + 100, y_pos + 100))
                    square = square.rotate(random.choice([0, 90, 180, 270]))
                    dest_imag.paste(square, (x_pos, y_pos))

            cropped = dest_imag

        if command == 'rotate':
            if width == height:
                cropped = cropped.rotate(random.choice([90, 180, 270]))
            else:
                cropped = cropped.rotate(180)

        if command == 'venetian':
            if random.randrange(100) < 50:
                for y_pos in range(0, height, 25):
                    slat = cropped.crop((0, y_pos, width, y_pos + 25))
                    slat = slat.transpose(Image.FLIP_TOP_BOTTOM)
                    cropped.paste(slat, (0, y_pos))
            else:
                for x_pos in range(0, width, 25):
                    slat = cropped.crop((x_pos, 0, x_pos + 25, height))
                    slat = slat.transpose(Image.FLIP_LEFT_RIGHT)
                    cropped.paste(slat, (x_pos, 0))

        if command == 'channel_rotate':
            r, g, b = Image.Image.split(cropped)
            cropped = Image.merge('RGB', random.choice([(g, b, r), (b, r, g)]))

        if command == 'channel_separate':
            # separate, misalign the channels, and combine
            r, g, b = Image.Image.split(cropped)

            if random.randrange(100) < 50:
                r.paste(r, (-20, 0))
                b.paste(b, (20, 0))
            else:
                r.paste(r, (0, -20))
                b.paste(b, (0, -20))

            cropped = Image.merge('RGB', (r, g, b))

        # Small chance of pasted with shift (but not when using the entire canvas)
        if random.randrange(100) < 20 and not full:
            self.cover.paste(cropped, (x_min + random.choice([-20,20]), y_min + random.choice([-20,20])))
        else:
            self.cover.paste(cropped, (x_min, y_min))

    def generate(self):
        # Random adjustments of the album/band
        if random.randrange(100) < 20:
            self.album_title = self.album_title.lower()
        if random.randrange(100) < 8:
            self.band_name = self.band_name.upper()
        if random.randrange(100) < 10:
            self.album_title = mispell.mispell(self.album_title)
        if random.randrange(100) < 20:
            self.band_name = mispell.mispell(self.band_name)
        if random.randrange(100) < 15:
            self.band_name = mispell.umlautify(self.band_name)
        if random.randrange(100) < 5:
            self.album_title = mispell.umlautify(self.album_title)

        # Randomly split multi-word band names
        spaces = len(self.band_name.split()) - 1
        split_name = ''
        if random.random() < (spaces * 0.1):
            newline_idx = random.randrange(spaces)
            words = self.band_name.split()
            idx = 0
            for w in words:
                split_name += w
                if idx == newline_idx:
                    split_name += '\n'
                else:
                    split_name += ' '
                idx += 1
            self.band_name = split_name

        # Shuffle the keywords, with the ones that appear in the album title appearing first.
        present_keywords = []
        missing_keywords = []

        for keyword in self.keywords:
            # Prioritise the ones in the actual title
            if self.album_title.lower().find(keyword.lower()) >= 0:
                present_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        random.shuffle(present_keywords)
        random.shuffle(missing_keywords)
        keyword_list = present_keywords + missing_keywords

        matching_keyword = 'NONE'
        for keyword in keyword_list:
            if self.fg.GetKeyword(keyword) is not None:
                matching_keyword = keyword
                break;

        art = Image.open('001.jpg')

        width, height = art.size

        # Get a random part of the image up to 800 x 600 pixels and paste it into the album art

        clip_width = min(800, width)
        clip_height = min(600, height)
        cropped = art.crop((0,0,clip_width,clip_height))
        self.cover.paste(cropped, ((800 - clip_width) // 2,100 + (600 - clip_height) // 2))

        # Select fonts for the album and band names, from a local directory.
        band_typeface = random.choice(glob.glob('./Fonts/*'))
        album_typeface = random.choice(glob.glob('./Fonts/*'))

        if self.inverted_colours:
            band_colour = [0, random.randrange(255), random.randrange(128)]
        else:
            band_colour = [255, random.randrange(255), random.randrange(128,256)]
        random.shuffle(band_colour)

        if self.inverted_colours:
            album_colour = [0, random.randrange(255), random.randrange(128)]
        else:
            album_colour = [255, random.randrange(255), random.randrange(128,256)]
        random.shuffle(album_colour)

        if random.randrange(100) < 40:
            album_colour = band_colour
        if random.randrange(100) < 20:
            album_typeface = band_typeface

        # Set up list of commands - it always contains drawing the band and album names, but can include filtering.
        # Shuffle the list and apply them.

        commands = ['band', 'title']
        filter_chances = {
            'convolve': 20,
            'blur': 20,
            'invert': 5,
            'quantize': 15,
            'grayscale': 15,
            'posterize': 10,
            'solarize': 15,
            'brightness': 15,
            'shuffle': 10,
            'rotate': 10,
            'spin': 10,
            'channel_rotate': 10,
            'channel_separate': 10,
            'jitter': 10,
            'venetian': 10,
            'edges': 15,
            'canny': 10
        }

        for c in filter_chances.keys():
            if random.randrange(100) < filter_chances[c]:
                commands.append(c)

        random.shuffle(commands)
        if [i for i in ['shuffle', 'rotate', 'quantize', 'spin', 'jitter', 'venetian'] if i in commands]:
            commands.remove('band')
            commands.remove('title')
            commands.append('band')
            commands.append('title')

        print(commands)

        for command in commands:
            if command == 'band':
                self.drawBand(band_typeface, tuple(band_colour))
            elif command == 'title':
                self.drawTitle(album_typeface, tuple(album_colour))
            else:
                self.filter(command, random.randrange(100) < 25 and command not in ['shuffle', 'jitter', 'venetian', 'spin'])


        # Print useful information
        print('Band: ' + self.band_name.replace('\n', ' ') + ' (' + band_typeface.split('\\')[-1] + ')')
        print('Album: ' + self.album_title + ' (' + album_typeface.split('\\')[-1] + ')')
        print('Artwork keyword: ' + matching_keyword)

        return self.cover.copy()

    def emit(self, filename='res.jpg'):
        self.cover.save(filename)
