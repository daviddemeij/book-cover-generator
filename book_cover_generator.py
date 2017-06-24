from matplotlib import pyplot as plt
import scipy.misc
import requests
import urllib
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

default_font_path = "/home/david/code/book-cover-generator/deepart-api/python/PlayfairDisplaySC-Regular.ttf"
default_title = "Harry Potter and the goblet of fire"
default_author = "J.K. Rowling"
def style_transfer(style_number, image_path):
    r = requests.post('http://turbo.deepart.io/api/post/',
                      data={'style': style_number,
                            'return_url': 'http://my.return/'},
                      files={'input_image': ('file.jpg', open(image_path, 'rb'), 'image/jpeg')})
    img = r.text
    link = ("http://turbo.deepart.io/media/output/%s.jpg" % img)
    print link

    max_num_seconds = 10

    for i in range(max_num_seconds):

        time.sleep(5)
        urllib.urlretrieve(link, "res.jpg")

        try:
            img = Image.open("res.jpg")
            img.close()
            break

        except:
            print "Try #" + str(
                i + 1) + ": Retrieving image failed (deepart-api needs more time). Trying again after 5s."
    return plt.imread("res.jpg")

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

def draw_text(img, output_size, maintitle, subtitle, author, font_path):
    draw = ImageDraw.Draw(img)
    H, W = output_size
    font_size = 300
    h_prev = 0
    h_max = 0

    for title_word in [maintitle, subtitle]:
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

    font = ImageFont.truetype(font_path, 100)
    w, h = draw.textsize(author, font=font)
    draw.text(((W - w) / 2, H - h - 40), author, font=font, fill=(255, 255, 255))
    img.save('sample-out.jpg')
    plt.imshow(img)
    return img

def generate_cover(input_image="harrypotter-content-image.jpg", title=default_title,
                   author=default_author, style_number=25, font_path=default_font_path, output_size=[1600, 1000]):
    img = plt.imread(input_image)

    # Crop image to a 1.6 aspect ratio
    if 1.6 * img.shape[0] > img.shape[1]:
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
    scipy.misc.imsave('content-image.jpg', img)

    img = style_transfer(style_number, 'content-image.jpg')
    img = scipy.misc.imresize(img, (output_size[0], output_size[1], 3))
    img = Image.fromarray(img, 'RGB')

    maintitle, subtitle = split_title(title)
    img = draw_text(img, output_size, maintitle, subtitle, author, font_path)
    return img

generate_cover()


