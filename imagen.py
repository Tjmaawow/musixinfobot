import asyncio
from functools import partial
from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont

example_photo = "https://picsum.photos/400/400"


class Imagen:
    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            width = font.getlength(test_line)

            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    async def download_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
                return None

    def _process_image_sync(self, image_bytes, title, artist):
        original_img = Image.open(BytesIO(image_bytes))

        W, H = 1200, 500

        background = original_img.copy().resize((W, H))
        background = background.filter(ImageFilter.GaussianBlur(radius=15))

        dark_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 100))

        background = background.convert("RGBA")
        canvas = Image.alpha_composite(background, dark_overlay)
        canvas = canvas.convert("RGB")

        cover_art = original_img.resize((400, 400))
        canvas.paste(cover_art, (50, 50))

        draw = ImageDraw.Draw(canvas)

        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            artist_font = ImageFont.truetype("arial.ttf", 40)
        except OSError:
            title_font = ImageFont.load_default()
            artist_font = ImageFont.load_default()

        text_x = 500
        max_text_width = W - text_x - 50

        wrapped_title = self.wrap_text(title, title_font, max_text_width)
        title_y = 100
        draw.multiline_text(
            (text_x, title_y), wrapped_title, font=title_font, fill="white", spacing=10
        )

        title_bbox = draw.multiline_textbbox(
            (text_x, title_y), wrapped_title, font=title_font, spacing=10
        )
        title_bottom_y = title_bbox[3]
        artist_y = title_bottom_y + 30

        wrapped_artist = self.wrap_text(artist, artist_font, max_text_width)

        draw.multiline_text(
            (text_x, artist_y),
            wrapped_artist,
            font=artist_font,
            fill="#dddddd",
            spacing=10,
        )

        bio = BytesIO()
        canvas.save(bio, "PNG")
        bio.seek(0)
        return bio

    async def genNew(self, title: str, artist: str, thumbail: str = example_photo):
        img_bytes = await self.download_image(thumbail)

        if not img_bytes:
            raise ValueError("Не удалось скачать изображение")

        result = await asyncio.to_thread(
            self._process_image_sync, img_bytes, title, artist
        )

        return result
