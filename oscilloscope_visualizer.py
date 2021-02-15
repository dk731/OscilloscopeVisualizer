import tkinter as tk
from tkinter import filedialog
import wave
import struct
import pygame as pg
import time
import winsound


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Main canvas")
        self.wid_list = dict()

        self.c = tk.Canvas(self, width=400, height=400)
        self.c.pack()
        self.f_index = 0
        self.f_data = []
        self.resizable(False, False)
        self.wid_list["new_window"] = tk.Button(
            self, text="LET'S GO", state=tk.DISABLED, command=self.create_window
        )
        self.wid_list["file_open"] = tk.Button(
            self, text="Open File", command=self.open_file
        )
        self.osc_surface = None
        self.file = None
        self.filename = None
        self.data_draw = []
        self.wid_pack()
        self.osc_win_width = 1000
        self.osc_win_height = 1000
        self.frame_rate = 0
        for num in range(0, 400, 5):
            self.f_data.append([num, num, num + 10, num + 10])

    def create_window(self):
        self.prev_frame = 0
        pg.init()
        self.main_draw_surf = pg.display.set_mode(
            (self.osc_win_width, self.osc_win_height)
        )
        pg.display.flip()
        self.draw_main_loop()

    def open_file(self):
        self.filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select file",
            filetypes=(("WAV files", "*.wav"), ("all files", "*.*")),
        )
        try:
            self.file = wave.open(self.filename, "rb")

            if not self.file.getnchannels() == 2:
                raise Exception(
                    "Invalid file format, only 2 channels files are supported"
                )

            self.wid_list["new_window"]["state"] = "normal"
        except Exception as e:
            print(e)
        self.frame_rate = self.file.getframerate()

    def next_frame(self):
        data = self.f_data[self.f_index]  # fetch frame data
        self.c.delete("all")  # clear canvas
        self.c.create_line(*data)  # draw new frame data
        self.f_index += 1  # increment frame index
        if self.f_index >= len(self.f_data):  # check and wrap if at end of sequence
            self.f_index = 0
        self.c.after(50, self.next_frame)  # call again after 50ms

    def wid_pack(self):
        for but in self.wid_list.values():
            but.pack()

    def draw_main_loop(self):
        running = True
        winsound.PlaySound(self.filename, winsound.SND_ASYNC)
        start_time = time.time()
        prev_time = start_time

        channel_width = self.file.getsampwidth()
        frame_size = channel_width * 2
        channel_max_val = 1 << (channel_width * 8)

        tmp_bytes = self.file.readframes(self.file.getnframes())

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            current_time = time.time()

            self.main_draw_surf.fill((0, 0, 0))
            ar = pg.PixelArray(self.main_draw_surf)

            for frame_i in range(
                round((prev_time - start_time) * self.frame_rate),
                round((current_time - start_time) * self.frame_rate),
            ):
                start_byte = frame_i * frame_size

                x = round(
                    (
                        int.from_bytes(
                            tmp_bytes[start_byte : (start_byte + channel_width)],
                            byteorder="little",
                            signed=True,
                        )
                        / channel_max_val
                        + 0.5
                    )
                    * (self.osc_win_width - 1)
                )

                y = round(
                    (
                        int.from_bytes(
                            tmp_bytes[
                                (start_byte + channel_width) : (start_byte + frame_size)
                            ],
                            byteorder="little",
                            signed=True,
                        )
                        / channel_max_val
                        + 0.5
                    )
                    * (self.osc_win_height - 1)
                )
                ar[x, y] = (0, 255, 0)
            del ar

            pg.display.flip()
            prev_time = current_time

        winsound.PlaySound(None, winsound.SND_PURGE)
        self.wid_list["new_window"]["state"] = "disabled"
        pg.display.quit()
        pg.quit()


app = App()
app.next_frame()
app.mainloop()
