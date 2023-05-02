from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import csv
import os
from os import getcwd
import numpy as np
import datetime
import locale
from pygrabber.dshow_graph import FilterGraph
from tktimepicker import SpinTimePickerOld, constants, AnalogPicker


locale.setlocale(locale.LC_TIME, "id_ID")
face_classifier = cv2.CascadeClassifier(
    'Haarcascades/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
graph = FilterGraph()


class App:
    def __init__(self):
        self.window = Tk()
        self.window.title("Absensi Siswa")
        self.window.geometry("800x400")
        self.window.resizable(0, 0)
        self.window.config(bg="white")
        self.main_page()
        self.training_data_set()

    def start(self):
        recognizer.read('Training/trainner.yml')
        self.update_setting()
        self.window.mainloop()

    def update_setting(self):
        with open(getcwd() + "/Data/setting.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row[0] == "camera":
                    self.default_camera = int(row[1])
                if row[0] == "jam_masuk":
                    self.default_jam_masuk = row[1]

        self.minimal_jam_masuk = datetime.datetime.strptime(
            self.default_jam_masuk, "%H:%M")

    def update_jam(self):
        self.label_jam.configure(
            text=datetime.datetime.now().strftime("%A, %d %B %Y %H:%M:%S"))
        self.label_jam.after(1000,  self.update_jam)

    def main_page(self):
        label_judul = Label(self.window, text="Absensi Siswa",
                            font=("Arial", 20), bg="white")
        label_judul.place(anchor="center", relx=.5, rely=.2)

        self.label_jam = Label(self.window, text=datetime.datetime.now().strftime("%A, %d %B %Y %H:%M:%S"),
                               font=("Arial", 16), bg="white")
        self.label_jam.place(anchor="center", relx=.5, rely=.3)

        button_absen_siswa = Button(self.window, text="Absen Siswa",
                                    font=("Arial", 16), bg="#126935", fg="white", borderwidth=0, cursor="hand2", width=30, command=self.absen_siswa_page)
        button_absen_siswa.place(anchor="center", relx=.5, rely=.45)

        button_daftar_siswa = Button(self.window, text="Daftar Siswa Baru",
                                     font=("Arial", 16), bg="#126935", fg="white", borderwidth=0, cursor="hand2", width=30, command=self.daftar_siswa_page)
        button_daftar_siswa.place(anchor="center", relx=.5, rely=.6)

        button_report_sabsen = Button(self.window, text="Laporan Absen",
                                      font=("Arial", 16), bg="#126935", fg="white", borderwidth=0, cursor="hand2", width=30, command=self.report_absen_page)
        button_report_sabsen.place(anchor="center", relx=.5, rely=.75)

        button_setting = Button(self.window, text="Setting",
                                font=("Arial", 16), bg="gray", fg="white", borderwidth=0, cursor="hand2", width=30, command=self.setting_page)
        button_setting.place(anchor="center", relx=.5, rely=.9)

        self.update_jam()

    def daftar_siswa_page(self):
        self.new_siswa_window = Toplevel(self.window)

        content = ttk.Frame(self.new_siswa_window, padding=20)
        content.grid(column=0, row=0)

        judul_new_siswa = ttk.Label(
            content, text="Daftar Siswa Baru", font=("Arial", 16))
        judul_new_siswa.grid(column=0, row=0, columnspan=6, pady=10)

        label_nis_siswa = ttk.Label(
            content, text="NIS", font=("Arial", 14))
        label_nis_siswa.grid(column=0, row=1)
        self.input_nis_siswa = ttk.Entry(
            content, width=30, font=("Arial", 12))
        self.input_nis_siswa.grid(column=1, row=1, padx=10)

        label_nama_siswa = ttk.Label(
            content, text="Nama Lengkap", font=("Arial", 14))
        label_nama_siswa.grid(column=0, row=2)
        self.input_nama_siswa = ttk.Entry(
            content, width=30, font=("Arial", 12))
        self.input_nama_siswa.grid(column=1, row=2, padx=10)

        self.label_error = ttk.Label(content)
        self.label_error.grid(column=1, row=3, pady=5)

        button_daftar_siswa = ttk.Button(
            content, text="Scan Wajah", padding=10, command=self.scan_wajah_page)
        button_daftar_siswa.grid(column=1, row=4, pady=5)

    def scan_wajah_page(self):
        if self.input_nis_siswa.get() == "" or self.input_nama_siswa.get() == "":
            self.label_error.configure(
                text="Mohon isi semua data!", foreground="red")
            return

        with open(getcwd() + "/Data/siswa.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                if not row:
                    continue
                if row[0] == self.input_nis_siswa.get():
                    self.label_error.configure(
                        text="NIS sudah ada!", foreground="red")
                    return

            csv_file.close()

        self.label_error.configure(text="")

        self.scan_wajah_window = Toplevel(self.new_siswa_window)
        self.camera = cv2.VideoCapture(self.default_camera)

        content = ttk.Frame(self.scan_wajah_window, padding=20)
        content.grid(column=0, row=0)

        self.label_scan_wajah = ttk.Label(content)
        self.label_scan_wajah.grid(column=0, row=0)

        self.label_persen_scan = ttk.Label(content, text="0%", font=(
            "Arial", 14), border=1, foreground="green")
        self.label_persen_scan.grid(column=1, row=0, padx=10)

        self.count_scan = 0
        self.scan_wajah_camera()

        self.scan_wajah_window.protocol(
            "WM_DELETE_WINDOW", self.closing_scan_camera)

    def scan_wajah_camera(self):
        ret, frame = self.camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.label_scan_wajah.imgtk = imgtk
        self.label_scan_wajah.configure(image=imgtk)
        self.label_scan_wajah.after(20, self.scan_wajah_camera)

        if len(faces) != 0:
            self.count_scan += 1
            self.label_persen_scan.configure(
                text=str(((self.count_scan/25)*100))+"%")

        for (x, y, w, h) in faces:
            cv2.imwrite("DataSet/User."+str(self.input_nis_siswa.get())+"." +
                        str(self.count_scan) + ".jpg", gray[y:y+h, x:x+w])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if self.count_scan > 24:
            with open(getcwd() + "/Data/siswa.csv", "a") as csv_file:
                csv_file.write("\n" + self.input_nis_siswa.get() +
                               "," + self.input_nama_siswa.get())
                csv_file.close()

            self.training_data_set()
            self.scan_wajah_window.destroy()
            self.new_siswa_window.destroy()
            self.camera.release()
            cv2.destroyAllWindows()

    def closing_scan_camera(self):
        if not hasattr(self, "scan_wajah_window"):
            return
        self.scan_wajah_window.destroy()
        self.camera.release()
        cv2.destroyAllWindows()

    def training_data_set(self):
        faces, Ids = self.getImagesAndLabels('DataSet')
        recognizer.train(faces, np.array(Ids))
        recognizer.write('Training/trainner.yml')

    def getImagesAndLabels(self, path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        Ids = []
        for imagePath in imagePaths:
            if (os.path.split(imagePath)[-1].split(".")[-1] != 'jpg'):
                continue

            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            Id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = face_classifier.detectMultiScale(imageNp)
            for (x, y, w, h) in faces:
                faceSamples.append(imageNp[y:y+h, x:x+w])
                Ids.append(Id)
        return faceSamples, Ids

    def absen_siswa_page(self):
        date_now = datetime.datetime.now()
        self.format_date_now = date_now.strftime("%d%m%Y")

        if not os.path.exists(getcwd() + "/Data/Absen/" + self.format_date_now + ".csv"):
            open(getcwd() + "/Data/Absen/" + self.format_date_now + ".csv", "x")

        self.absen_siswa_window = Toplevel(self.window)
        self.absen_siswa_window.resizable(0, 0)
        self.camera = cv2.VideoCapture(self.default_camera)

        content = ttk.Frame(self.absen_siswa_window, padding=20)
        content.grid(column=0, row=0)

        self.label_absen_wajah = ttk.Label(content)
        self.label_absen_wajah.grid(column=0, row=0)

        self.label_cek_absen = ttk.Label(
            content, font=("Arial", 16))
        self.label_cek_absen.grid(column=0, row=1, pady=10)

        self.absen_siswa_camera()
        self.count_absen = 0

        self.absen_siswa_window.protocol("WM_DELETE_WINDOW",
                                         self.closing_absen_camera)

    def absen_siswa_camera(self):
        ret, frame = self.camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if faces == ():
            self.label_cek_absen.configure(text="")

        for (x, y, w, h) in faces:
            id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            print(id, conf)

            if conf >= 45 and conf <= 70:
                cv2.rectangle(rgb_img, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)
                name = self.get_name_from_id(id)
                cv2.putText(rgb_img, name, (x, y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), thickness=2)
                if not self.check_sudah_absen(id):
                    self.label_cek_absen.configure(
                        text="Memproses Absen", foreground="orange")
                    self.count_absen += 1

                    if self.count_absen > 25:
                        with open(getcwd() + "/Data/Absen/" + self.format_date_now + ".csv", "a") as csv_file:
                            csv_file.write("\n" + str(id) + "," + name + "," +
                                           str(datetime.datetime.now().strftime("%H:%M:%S")))
                        self.count_absen = 0
            else:
                cv2.rectangle(rgb_img, (x, y), (x + w, y + h), (255, 0, 0))
                self.label_cek_absen.configure(
                    text="Wajah tidak dikenali", foreground="red")
                self.count_absen = 0

        img = Image.fromarray(rgb_img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label_absen_wajah.imgtk = imgtk
        self.label_absen_wajah.configure(image=imgtk)
        self.label_absen_wajah.after(20, self.absen_siswa_camera)

    def closing_absen_camera(self):
        if not hasattr(self, "absen_siswa_window"):
            return
        self.absen_siswa_window.destroy()
        self.camera.release()
        cv2.destroyAllWindows()

    def check_sudah_absen(self, id):
        with open(getcwd() + "/Data/Absen/" + self.format_date_now + ".csv", "r+") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                if row:
                    if row[0] == str(id):
                        name = self.get_name_from_id(id)
                        self.label_cek_absen.configure(
                            text=name + " berhasil absen", foreground="green")
                        self.count_absen = 0
                        return True
                else:
                    continue

            return False

    def get_name_from_id(self, id):
        with open(getcwd() + "/Data/siswa.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                if row:
                    if row[0] == str(id):
                        return row[1]
                else:
                    continue

    def report_absen_page(self):
        self.report_absen_window = Toplevel(self.window)

        self.content_report_absen = ttk.Frame(
            self.report_absen_window, padding=20)
        self.content_report_absen.pack(fill=BOTH, expand=YES)

        judul = ttk.Label(self.content_report_absen,
                          text="Laporan Absen", font=("Arial", 16))
        judul.pack(fill=BOTH, expand=YES, side=TOP)

        frame_label = ttk.Frame(self.content_report_absen)
        frame_label.pack(fill=BOTH, expand=YES, side=TOP)

        label_tanggal = ttk.Label(
            frame_label, text="Tanggal / Hari", font=("Arial", 13))
        label_tanggal.pack(side=LEFT)

        label_siswa = ttk.Label(
            frame_label, text="Siswa yang absen", font=("Arial", 13))
        label_siswa.pack(fill="none", side=RIGHT)

        self.frame_list_dates()
        self.isi_list_box_date()
        self.frame_list_siswa()
        self.on_choose_date()

    def frame_list_dates(self):
        # FRAME TANGGAL
        fr_kiri = Frame(self.content_report_absen, bd=10)
        fr_kiri.pack(expand=YES, side=LEFT, fill=BOTH)

        scroll = Scrollbar(fr_kiri, orient=VERTICAL)
        self.list_box_date = Listbox(fr_kiri, width=30,
                                     yscrollcommand=scroll.set)
        self.list_box_date.pack(fill=Y, side=LEFT)
        scroll.configure(command=self.list_box_date.yview)
        scroll.pack(side=LEFT, fill=Y)

        self.list_box_date.bind('<ButtonRelease-1>', self.on_choose_date)
        self.list_box_date.bind('<KeyRelease>', self.on_choose_date)
        self.list_box_date.configure(font=("Arial", 12))

    def frame_list_siswa(self):
        fr_kanan = Frame(self.content_report_absen, bd=10)
        fr_kanan.pack(expand=YES, side=RIGHT, fill=BOTH)

        scroll = Scrollbar(fr_kanan, orient=VERTICAL)
        self.list_box_siswa = Listbox(fr_kanan, width=70,
                                      yscrollcommand=scroll.set)
        self.list_box_siswa.pack(fill=Y, side=RIGHT)
        self.list_box_siswa.configure(font=("Arial", 12))
        scroll.configure(command=self.list_box_siswa.yview)
        scroll.pack(side=RIGHT, fill=Y)

    def on_choose_date(self, event=None):
        self.list_box_siswa.delete(0, END)
        index = int(self.list_box_date.curselection()[0])
        absen_siswa = []

        with open(getcwd() + "/Data/Absen/" + self.list_dates[index], "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                if row:
                    absen_siswa.append(row)

        for idx, siswa in enumerate(absen_siswa):
            nis = siswa[0]
            nama = siswa[1]
            jam_masuk = siswa[2]
            format_jam_masuk = datetime.datetime.strptime(
                jam_masuk, "%H:%M:%S")
            telat = format_jam_masuk.time() >= self.minimal_jam_masuk.time()
            self.list_box_siswa.insert(
                END,  nis + " - " + nama + " - " + jam_masuk + " - " + ("Telat" if telat else "Tepat Waktu"))
            self.list_box_siswa.itemconfigure(
                idx, foreground="red" if telat else "green")

    def isi_list_box_date(self):
        path = getcwd() + "/Data/Absen"
        self.list_dates = os.listdir(path)

        for date in self.list_dates:
            tanggal = date.split(".")[0]
            tanggal = datetime.datetime.strptime(tanggal, "%d%m%Y")
            tanggal = tanggal.strftime("%A, %d %B %Y")
            self.list_box_date.insert(END, str(tanggal))

        self.list_box_date.selection_set(0)

    def setting_page(self):
        self.closing_scan_camera()
        self.closing_absen_camera()

        self.setting_window = Toplevel(self.window)
        self.list_camera = graph.get_input_devices()

        content = ttk.Frame(self.setting_window, padding=20)
        content.grid(column=0, row=0)

        judu_setting = ttk.Label(
            content, text="Pengaturan", font=("Arial", 16))
        judu_setting.grid(column=0, row=0)

        label_default_jam = ttk.Label(
            content, text="Jam Masuk", font=("Arial", 12))
        label_default_jam.grid(column=0, row=1, pady=10)
        self.choosed_time = AnalogPicker(content, type=constants.HOURS24)
        self.choosed_time.setHours(self.minimal_jam_masuk.hour)
        self.choosed_time.setMinutes(self.minimal_jam_masuk.minute)
        self.choosed_time.grid(column=1, row=1, padx=10, columnspan=2, pady=10)

        label_default_camera = ttk.Label(
            content, text="Default Camera", font=("Arial", 12))
        label_default_camera.grid(column=0, row=2, pady=10)

        self.choosed_camera = StringVar()
        print(self.list_camera[self.default_camera])

        self.option_default_camera = ttk.OptionMenu(
            content, self.choosed_camera, self.list_camera[0],  *self.list_camera)
        self.choosed_camera.set(self.list_camera[self.default_camera])
        self.option_default_camera.grid(
            column=1, row=2, padx=10, columnspan=2, pady=10)

        button_save = ttk.Button(content, text="Save",
                                 command=self.set_default_camera)
        button_save.grid(column=1, row=3, columnspan=2, pady=10)

    def set_default_camera(self):
        camera = self.choosed_camera.get()
        jam = self.choosed_time.time()
        idx_camera = self.list_camera.index(camera)
        format_jam = "{}:{}".format(*jam)

        with open(getcwd() + "/Data/setting.csv", "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_file.write("camera" + "," + str(idx_camera))
            csv_file.write("\njam_masuk" + "," + format_jam)

        self.update_setting()
        self.setting_window.destroy()


app = App()
app.start()
