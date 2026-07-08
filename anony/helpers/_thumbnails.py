# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.

import os
import aiohttp
import textwrap
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)

from anony import config
from anony.helpers import Track

CANVAS_SIZE = (1280, 720)
FRAME_RECT = (180, 110, 1100, 610)
ART_RECT = (110, 145, 530, 565)
INFO_RECT = (285, 470, 995, 650)
TITLE_AREA_WIDTH = 316


class Thumbnail:
    def __init__(self):
        self.fill = (255, 255, 255)
        self.font1 = ImageFont.truetype(
            "anony/helpers/Poppins-ExtraBold.ttf", 65
        )
        self.font2 = ImageFont.truetype(
            "anony/helpers/Raleway-Bold.ttf", 30
        )
        self.font3 = ImageFont.truetype(
            "anony/helpers/Raleway-Bold.ttf", 22
        )

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                open(output_path, "wb").write(await resp.read())
            return output_path

    def fit_image(self, image, size):
        return ImageOps.fit(
            image,
            size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    def add_round_corners(self, image, radius):
        rounded = image.convert("RGBA")
        mask = Image.new("L", rounded.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            (0, 0, rounded.size[0], rounded.size[1]),
            radius=radius,
            fill=255,
        )
        output = Image.new("RGBA", rounded.size, (0, 0, 0, 0))
        output.paste(rounded, (0, 0), mask)
        return output

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            os.makedirs("cache", exist_ok=True)

            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"

            if os.path.exists(output):
                os.remove(output)

            await self.save_thumb(temp, song.thumbnail)

            youtube = Image.open(temp).convert("RGBA")

            from PIL import ImageStat

            small = youtube.resize((50, 50))
            r, g, b = ImageStat.Stat(small).mean[:3]

            glow_color = (
               int(r),
               int(g),
               int(b),
               80
            )

            background = self.fit_image(youtube, CANVAS_SIZE)
            background = background.filter(ImageFilter.GaussianBlur(30))
            background = ImageEnhance.Brightness(background).enhance(0.50)

            canvas = Image.new("RGBA", CANVAS_SIZE, (0,0,0,255))
            canvas.alpha_composite(background)
            
            glass = Image.new("RGBA", CANVAS_SIZE, (0,0,0,0))
            gdraw = ImageDraw.Draw(glass)

            gdraw.rounded_rectangle(
                (60, 80, 1220, 640),
                radius=42,
                fill=(255,255,255,30),
                outline=(255,255,255,120),
                width=2
            )

            glass = glass.filter(
               ImageFilter.GaussianBlur(2)
            )

            canvas.alpha_composite(glass)
            
            artwork_size = (
                ART_RECT[2] - ART_RECT[0],
                ART_RECT[3] - ART_RECT[1],
            )

            artwork = self.add_round_corners(
                self.fit_image(youtube, artwork_size),
                35,
            )

            glass = Image.new("RGBA", CANVAS_SIZE, (0,0,0,0))
            ...
            canvas.alpha_composite(glass)

            canvas.alpha_composite(
               artwork,
               (ART_RECT[0], ART_RECT[1]),
            )

            gdraw.rounded_rectangle(
                (20, 60, 1260, 680),
                radius=50,
                fill=(255,255,255,55)
            )

            glass = glass.filter(ImageFilter.GaussianBlur(15))
            canvas.alpha_composite(glass)

            draw = ImageDraw.Draw(canvas)

            duration = song.duration
            views = song.view_count
            
            text_x = 610

            title = (
                 song.title[:16] + "..."
                 if len(song.title) > 16
                 else song.title
            )

            channel = (
               song.channel_name[:27] + "..."
               if len(song.channel_name) > 27
               else song.channel_name
            )

            title_color = (255, 255, 255)
            channel_color = (255, 255, 255)
            views_color = (255, 255, 255)

            import textwrap

            draw.text(
                (560, 120),
                "RAJA-BABU",
                font=self.font3,
                fill=(220,220,220)
            )

            lines = textwrap.wrap(title.upper(), width=14)

            line1 = lines[0] if len(lines) > 0 else ""
            line2 = lines[1] if len(lines) > 1 else ""

            draw.text(
                (600, 180),
                line1,
                font=ImageFont.truetype(
                   "anony/helpers/Poppins-ExtraBold.ttf", 55
                ),
            fill=(255,255,255)
            )

            if line2:
                draw.text(
                    (600, 250),
                    line2,
                    font=ImageFont.truetype(
                      "anony/helpers/Poppins-ExtraBold.ttf", 55
                    ),
                    fill=(255,255,255)
               )

            draw.text(
                (600, 340),
                "FEEL THE LOVE",
                font=ImageFont.truetype(
                   "anony/helpers/Poppins-ExtraBold.ttf", 55
                ),
                fill=(255,220,0)
            )

            draw.text(
                (600, 430),
                f"YouTube | {views}",
                font=self.font2,
                fill=(220,220,220)
            )

            draw.rounded_rectangle(
                (600, 520, 1150, 530),
                radius=8,
                fill=(255,255,255,60)
            )

            draw.rounded_rectangle(
                (600, 520, 860, 530),
                radius=8,
                fill=(255,255,255)
            )

            draw.ellipse(
              (845,507,873,535),
              fill=(255,255,255)
            )

            draw.text(
                (600, 540),
                "00:00",
                font=self.font3,
                fill=(255,255,255)
            )

            draw.text(
                (1120, 540),
                duration,
                font=self.font3,
                fill=(255,255,255)
            )

            canvas.save(output, format="PNG", optimize=True)

            try:
                os.remove(temp)
            except:
                pass

            return output

        except Exception:
            return config.DEFAULT_THUMB


