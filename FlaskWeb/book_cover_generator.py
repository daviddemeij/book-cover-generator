from matplotlib import pyplot as plt
import scipy.misc
import requests
import urllib
import time
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import base64
import cStringIO

def style_transfer(style_number, image_path):
    r = requests.post('http://turbo.deepart.io/api/post/',
                      data={'style': style_number,
                            'return_url': 'http://my.return/'},
                      files={'input_image': ('file.jpg', open(image_path, 'rb'), 'image/jpeg')})
    img = r.text
    link = ("http://turbo.deepart.io/media/output/%s.jpg" % img)
    print link

    max_num_seconds = 20
    style_transfer_path = os.path.join(os.curdir, "results.jpg")
    print "Trying to store style transfer result at %s ..." % style_transfer_path
    for i in range(max_num_seconds):
        time.sleep(2)
        urllib.urlretrieve(link, style_transfer_path)
        try:
            img = Image.open(style_transfer_path)
            img.close()
            break
        except:
            print "Try #" + str(
                i + 1) + ": Retrieving image failed (deepart-api needs more time). Trying again after 2s."
    return plt.imread(style_transfer_path)

def split_title(title):
    writing_subtitle = False
    title = title.split(" ")
    total_length = 0
    maintitle = ""
    subtitle = ""
    for i, title_word in enumerate(title):
        total_length += len(title_word)
        if i >= 3 or total_length > 12 and writing_subtitle == False:
            writing_subtitle = True
            subtitle += title_word + " "
        elif writing_subtitle:
            subtitle += title_word + " "
        else:
            maintitle += title_word + " "
    print "Maintitle: ", maintitle
    print "Subtitle: ", subtitle
    return maintitle, subtitle

def draw_text(img, output_size, maintitle, subtitle, author, font_paths):
    draw = ImageDraw.Draw(img)
    H, W = output_size
    font_size = 300
    h_prev = 0
    h_max = 0
    for title_word, font_path in zip([maintitle, subtitle], font_paths[:2]):
        font = ImageFont.truetype(font_path, font_size)
        w, h = draw.textsize(title_word, font=font)
        while w + 40 > W:
            font_size -= 3
            font = ImageFont.truetype(font_path, font_size)
            w, h = draw.textsize(title_word, font=font)
        if (h > h_max):
            h_max = h
        # font = ImageFont.truetype(<font-file>, <font-size>)
        # draw.text((x, y),"Sample Text",(r,g,b))
        x = (W - w) / 2
        y = H / 2 + h_prev
        shadowcolor = (0, 0, 0)
        if font_size > 140:
            border_thickness = 6
        else:
            border_thickness = 4
        h_prev += 1.0 * h
        for j in range(border_thickness):
            # thicker border
            draw.text((x - j, y - j), title_word, font=font, fill=shadowcolor)
            draw.text((x + j, y - j), title_word, font=font, fill=shadowcolor)

        # now draw the text over it
        draw.text((x, y), title_word, (255, 255, 255), font=font)
    font = ImageFont.truetype(font_paths[2], 100)
    w, h = draw.textsize(author, font=font)
    draw.text(((W - w) / 2, H - h - 40), author, font=font, fill=(255, 255, 255))
    return img

def generate_cover(input_image="harrypotter-content-image.jpg", title="Harry Potter and the Goblet of Fire",
                   author="J.K. Rowling", genre="fantasy", output_size=(1600, 1000)):
    genre = genre.lower().strip(" ")
    genre_to_style = {
        "thriller": 47,
        "romance": 1,
        "kids": 9,
        "mystery": 37,
        "sci-fi": 17,
        "fantasy": 35
    }
    if genre not in genre_to_style.keys():
        print "Warning: genre not found, using thriller!"
        genre = "thriller"
    style_number = genre_to_style[genre]
    main_font_path = os.path.join(os.curdir, "fonts/"+genre+"_main.ttf")
    sub_font_path = os.path.join(os.curdir, "fonts/"+genre+"_sub.ttf")
    author_font_path = os.path.join(os.curdir, "fonts/"+genre+"_author.ttf")

    print "loading fonts %s, %s and %s ..." % (main_font_path, sub_font_path, author_font_path)

    img = plt.imread(input_image)
    # Crop image to a 1.6 aspect ratio
    if img.shape[0] > 1.6*img.shape[1]:
        width = [0, img.shape[1]]
        difference = (img.shape[0] - 1.6 * img.shape[1])
        height = [int(difference / 2.0), int(1.6 * img.shape[1] + difference / 2.0)]
    else:
        height = [0, img.shape[0]]
        difference = img.shape[1] - img.shape[0] / 1.6
        width = [int(difference / 2.0), int(img.shape[0] / 1.6 + difference / 2.0)]
    print width, height
    img = img[height[0]:height[1], width[0]:width[1]]

    # Resize image to desired output size
    img = scipy.misc.imresize(img, (output_size[0], output_size[1], 3))
    content_image_path = os.path.join(os.curdir, 'content-image.jpg')
    print "Saving content image at %s ..." % content_image_path
    scipy.misc.imsave(content_image_path, img)

    img = style_transfer(style_number, 'content-image.jpg')
    img = scipy.misc.imresize(img, (output_size[0], output_size[1], 3))
    img = Image.fromarray(img, 'RGB')

    maintitle, subtitle = split_title(title)
    img = draw_text(img, output_size, maintitle, subtitle, author,
                    font_paths=[main_font_path, sub_font_path, author_font_path])

    buffer = cStringIO.StringIO()
    img.save(buffer, format="JPEG")
    img_str = str(base64.b64encode(buffer.getvalue()))

    return img_str
