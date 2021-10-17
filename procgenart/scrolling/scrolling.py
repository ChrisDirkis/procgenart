import PIL.Image
import PIL.ImageDraw

import random
import math

def hash(a):
    a = (a ^ 61) ^ (a >> 16)
    a &= 0xFFFFFFFF
    a = a + (a << 3)
    a &= 0xFFFFFFFF
    a = a ^ (a >> 4)
    a &= 0xFFFFFFFF
    a = a * 0x27d4eb2d
    a &= 0xFFFFFFFF
    a = a ^ (a >> 15)
    a &= 0xFFFFFFFF
    return a


width = 64
height = 64

steps = 256

resize_multiplier = 4

amplitude_range_max = 15
#value_noise_max = 4


def create_image(field, offset):
    image = PIL.Image.new("HSV", (width, height))
    for x in range(width):
        d = ((x + offset) % steps) / steps * 2 * math.pi
        i = int(math.cos(d) * width / 2) 
        j = int(math.sin(d) * width / 2) 

        for y in range(height):
            k = int(y - (height / 2) * 2 * math.pi)
            image.putpixel((x, y), field(i, j, k))
    return image


def generate(file, seed):
    random.seed(seed)

    #value_noise_amplitude = random.triangular(0, value_noise_max) + 2
    hue_amplitude = 5 + random.triangular(0, amplitude_range_max)

    base_hue = random.randint(0, 255)
    base_sat = random.randint(180, 225)
    base_value = random.randint(100, 230)

    # hash_offset_1 = random.randint(0, 0xFFF)
    # hash_offset_2 = random.randint(0, 0xFFF)

    x_off = random.randint(-1000, 1000)
    y_off = random.randint(-1000, 1000)
    z_off = random.randint(-1000, 1000)

    a_div_1 = random.random() * 20 + 5
    a_div_2 = random.random() * 20 + 5
    b_div_1 = random.random() * 20 + 5
    b_div_2 = random.random() * 20 + 5
    c_div_1 = random.random() * 20 + 5
    c_div_2 = random.random() * 20 + 5

    a_add = random.random() * 20
    b_add = random.random() * 20
    c_add = random.random() * 20

    x_mult = random.uniform(0.03, 0.06)
    y_mult = random.uniform(0.03, 0.06)
    z_mult = random.uniform(0.03, 0.06)

    value_mult = random.uniform(0.01, 0.02)

    def field(x, y, z):
        a = (x + y) + a_add + x_off + y_off
        b = (y + z) + b_add + y_off + z_off
        c = (z + x) + c_add + z_off + x_off
        hue_off_1 = ((math.sin(a / a_div_1) + math.cos(b / b_div_1) + math.sin(c / c_div_1)) / 3 - 0.5) * hue_amplitude * 2
        hue_off_2 = ((math.cos(a / a_div_2) + math.sin(b / b_div_2) + math.cos(c / c_div_2)) / 3 - 0.5) * hue_amplitude * 2
        
        hue = base_hue + int((hue_off_1 + hue_off_2) / 2)
        hue %= 255
        hue += 255
        hue %= 255

        value_wave = int(math.cos((x + y + z) * value_mult) * 15)

        hole = math.pow(abs(math.sin((x + a_add) * x_mult) * math.sin((y + b_add) * y_mult) * math.sin((z + c_add)* z_mult)), 5)
        
        value = int((base_value + value_wave) * (1 - hole)) 

        #value = int(base_value + (hash(x + y * hash_offset_1 + z * hash_offset_1 * hash_offset_2) / 0xFFFFFFFF - 0.5) * value_noise_amplitude * 2)
        return (hue, base_sat, value)

    images = [create_image(field, offset) for offset in range(steps)]
    images = [image.convert("RGB") for image in images]
    images = [image.resize((width * resize_multiplier, height * resize_multiplier)) for image in images]

    images[0].save(file, "WEBP", save_all=True, append_images=images[1:], duration=33, loop=0, quality=100)