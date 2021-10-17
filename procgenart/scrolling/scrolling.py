import PIL.Image
def generate(file, seed):

    image = PIL.Image.new("RGB", (256, 256))
    image.putpixel((128, 128), (255, 255, 255))

    image.save(file, "PNG")