from tkinter import *
from PIL import ImageTk, Image, ImageFilter, ImageDraw, ImageFont
from tkinter import filedialog

FONT = ImageFont.truetype("arial.ttf", 20, encoding="unic")
MAX_SIZE = (800, 526)
WATERMARK_SIZE = (100, 180)


class App:
    def __init__(self, window):
        window.title("Image Watermaking")
        self.frame = Frame(window)
        self.frame.config(padx=20, pady=20)
        self.frame.pack()

        self.frame_down = Frame(window)
        self.frame_down.pack()

        self.new_img = None
        self.watermark = None

        # keep ImageTk for canvas
        self.new_watermarks = []
        self.new_canvases = []
        # keep images for save function
        self.images = []
        self.entries = []
        # keep text for save function
        self.text = []
        self.current_canvas = None
        # keep original images for flip and b_and_w_image functions
        self.original_images = []
        self.degree = 45

        self.photo_image = PhotoImage(file='start_img.png')
        self.canvas = Canvas(self.frame_down, width=480, height=526, highlightthickness=0)
        self.front_image = self.canvas.create_image(0, 0, anchor='nw', image=self.photo_image)
        self.canvas.pack(expand=1, fill=BOTH)

        self.entry = Entry()

        self.open_button = Button(self.frame, text='Choose file', command=self.choose_img)
        self.open_button.grid(column=0, row=1)

        self.save_button = Button(self.frame, text='Save', bg='lightgreen', command=self.save)
        self.remove_button = Button(self.frame, text='Remove', command=self.remove)

        self.add_logo_button = Button(self.frame, text='Add Logo', command=self.add_watermark)
        self.add_text_button = Button(self.frame, text='Add Text', command=self.add_text)

        # from icons8.ru
        self.increase_icon = PhotoImage(file='increase.png')
        self.reduce_icon = PhotoImage(file='reduce.png')
        self.mono_icon = PhotoImage(file='monochrome.png')
        self.flip_icon = PhotoImage(file='flip.png')

        self.menu = Menu(tearoff=0, borderwidth=1)
        self.menu.add_command(image=self.reduce_icon, command=self.reduce_img)
        self.menu.add_command(image=self.increase_icon, hidemargin=1, command=self.increase_img)
        self.menu.add_command(image=self.mono_icon, command=self.b_and_w_image)
        self.menu.add_command(image=self.flip_icon, command=lambda: self.flip_image(self.degree))
        self.menu.add_command(label='blur', command=self.blur_image)

        self.canvas.bind_class("Canvas", "<B1-Motion>", self.drag)
        self.entry.bind_class("Entry", "<B1-Motion>", self.drag)
        self.canvas.bind_class("Canvas", "<ButtonPress-3>", self.click)

    # load image from computer
    def open_image(self):
        filetypes = (('jpg files', '*.jpg'), ('jpeg files', '*.jpeg'), ('png files', '*.png'))
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath != "":
            with Image.open(filepath) as im:
                im.load()
                return im

    # save created image to computer
    def save_image(self):
        filepath = filedialog.asksaveasfilename(defaultextension='jpg')
        if filepath != "":
            if self.new_img.mode == "RGBA":
                self.new_img.save(f'{filepath}.png')
            else:
                self.new_img.save(f'{filepath}.jpg')

    # drag canvases
    def drag(self, event):
        mouse_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        mouse_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        if event.widget in self.new_canvases or event.widget in self.entries:
            event.widget.place(x=mouse_x, y=mouse_y)

    # determine current canvas by clicking right mouse button, add menu
    def click(self, event):
        if event.widget in self.new_canvases:
            self.current_canvas = event.widget
            self.menu.post(event.x_root, event.y_root)

    # choose main image
    def choose_img(self):
        self.new_img = self.open_image()
        if self.new_img is not None:
            max_size = MAX_SIZE
            self.new_img.thumbnail(max_size)
            self.photo_image = ImageTk.PhotoImage(image=self.new_img)
            self.canvas.itemconfig(self.front_image, image=self.photo_image)
            self.canvas['width'] = self.new_img.size[0]
            self.canvas['height'] = self.new_img.size[1]
            self.add_logo_button.grid(column=3, row=1)
            self.add_text_button.grid(column=4, row=1)
            self.save_button.grid(column=6, row=1)
            self.remove_button.grid(column=5, row=1)

    # add images on main image
    def add_watermark(self):
        new_image = self.open_image().convert('RGBA')
        if new_image is not None:
            self.original_images.append(new_image)
            self.images.append(new_image)
            max_size = WATERMARK_SIZE
            watermark = new_image.copy()
            watermark.thumbnail(max_size)
            w = watermark.size[0]
            h = watermark.size[1]
            self.watermark = ImageTk.PhotoImage(watermark)
            self.new_watermarks.append(self.watermark)

            new_canvas = Canvas(self.frame_down, width=w, height=h, highlightthickness=0, bg='white')
            self.front_image = new_canvas.create_image(0, 0, anchor=NW, image=self.watermark)
            new_canvas.place(x=0, y=0)
            self.new_canvases.append(new_canvas)

    # change image on added canvas on main image
    def change_canvas(self, size):
        index = self.new_canvases.index(self.current_canvas)
        if size is None:
            size = (int(self.current_canvas['width']), int(self.current_canvas['height']))
        image_reduced = self.images[index].copy()
        image_reduced.thumbnail(size)

        self.new_watermarks[index] = ImageTk.PhotoImage(image_reduced)
        self.current_canvas.itemconfig(self.front_image, image=self.new_watermarks[index])
        self.current_canvas['width'] = image_reduced.size[0]
        self.current_canvas['height'] = image_reduced.size[1]

    # flip added images at 45
    def flip_image(self, degree):
        index = self.new_canvases.index(self.current_canvas)
        self.images[index] = self.original_images[index].rotate(degree, expand=1)
        self.change_canvas(None)
        self.degree += 45

    # blur added image
    def blur_image(self):
        index = self.new_canvases.index(self.current_canvas)
        self.images[index] = self.images[index].filter(ImageFilter.BoxBlur(5))
        self.change_canvas(None)

    # change added image to L mode
    def b_and_w_image(self):
        index = self.new_canvases.index(self.current_canvas)
        if self.images[index].mode == 'RGBA':
            self.images[index] = self.images[index].convert("L")
            self.images[index].filter(ImageFilter.EMBOSS)
        else:
            self.images[index] = self.original_images[index]
        self.change_canvas(None)

    # add Entry for text input
    def add_text(self):
        entry = Entry(self.frame_down, justify='left')
        entry.insert(0, 'Your text')
        entry.place(x=0, y=0)
        self.entries.append(entry)

    # reduce added image
    def reduce_img(self):
        new_width = int(self.current_canvas['width']) - 20
        new_height = int(self.current_canvas['height']) - 20
        max_size = (new_width, new_height)
        self.change_canvas(max_size)

    # increase added image
    def increase_img(self):
        new_width = int(self.current_canvas['width']) + 20
        new_height = int(self.current_canvas['height']) + 20
        max_size = (new_width, new_height)
        self.change_canvas(max_size)

    # remove all added images and text
    def remove(self):
        for canvas in self.new_canvases:
            canvas.destroy()
        self.new_canvases.clear()
        self.images.clear()
        self.new_watermarks.clear()
        self.original_images.clear()
        self.degree = 45
        for entry in self.entries:
            entry.destroy()

    # paste added images and text on main image and save
    def save(self):
        for i in range(len(self.new_canvases)):
            new_mark = self.images[i]
            size = int(self.new_canvases[i]['width']), int(self.new_canvases[i]['height'])
            new_mark.thumbnail(size)
            x = int(self.new_canvases[i].place_info()['x'])
            y = int(self.new_canvases[i].place_info()['y'])
            self.new_canvases[i].destroy()
            self.new_img.paste(new_mark, (x, y), new_mark.convert('RGBA'))

        drawer = ImageDraw.Draw(self.new_img)
        for entry in self.entries:
            x = int(entry.place_info()['x'])
            y = int(entry.place_info()['y'])
            text = entry.get()
            drawer.text((x, y), text,  font=FONT)
            entry.destroy()

        self.photo_image = ImageTk.PhotoImage(image=self.new_img)
        self.canvas.itemconfig(self.front_image, image=self.photo_image)

        self.save_image()
        self.remove()


root = Tk()
app = App(window=root)
root.mainloop()

