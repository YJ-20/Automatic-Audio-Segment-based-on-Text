from tkinter import filedialog, StringVar, IntVar
import tkinter as tk
import os
from align_and_segment import main_for_ui

class GUI():
    def __init__(self, cfg):
        self.window = tk.Tk()
        self.cfg = cfg

        self.selected_file = StringVar()
        self.selected_file2 = StringVar()
        self.output_fname = StringVar()
        self.status_text = StringVar()
        self.selected_sheet = IntVar()
        self.lang = StringVar()
        self._init()

        self.window.mainloop()

    def _init(self):
        self.window.title(self.cfg["title"])

        g = self.cfg["geometry"]
        self.window.geometry(f"{g['width']}x{g['height']}+{g['x']}+{g['y']}")
        if self.cfg["resizable"]:
            self.window.resizable()

        # menu settings
        menubar = tk.Menu(self.window)
        menu_1 = tk.Menu(menubar, tearoff=0)
        menu_1.add_command(label="종료", command=self.close)
        menubar.add_cascade(label="File", menu=menu_1)

        self.window.config(menu=menubar)

        # ui settings
        # text file
        input_frame = tk.Frame(self.window, width=300, height=100)
        input_frame.pack()
        label = tk.Label(input_frame, text="텍스트 파일 (*.txt, *.csv, *.xlsx)", width=25)
        label.grid(column=0, row=0, padx=10, pady=5)
        textbox = tk.Entry(input_frame, width=50, textvariable=self.selected_file)
        textbox.config(state="disabled")
        textbox.grid(column=1, row=0, padx=10, pady=5)

        action = tk.Button(input_frame, text="파일 선택", command=self.select_file)
        action.grid(column=2, row=0, padx=10, pady=5)
        
        option_frame = tk.Frame(self.window, width=300, height=80)
        option_frame.pack(after=input_frame, anchor="ne")
        option_label = tk.Label(option_frame, text="시트번호 :", width=10)
        option_label.grid(column=0, row=0, padx=10, pady=5)
        textbox = tk.Entry(option_frame, width=3, textvariable=self.selected_sheet)
        textbox.grid(column=1, row=0, padx=10, pady=5)
        self.selected_sheet.set(0)
        description = tk.Message(option_frame, text="(*.xlsx만 적용됨)", aspect=1000)
        description.grid(column=2, row=0)

        option_frame2 = tk.Frame(self.window, width=300, height=80)
        option_frame2.pack(after=option_frame, anchor="ne")
        option_label2 = tk.Label(option_frame2, text="언어코드 :", width=10)
        option_label2.grid(column=0, row=0, padx=10, pady=5)
        textbox2 = tk.Entry(option_frame2, width=3, textvariable=self.lang)
        textbox2.grid(column=1, row=0, padx=10, pady=5)
        self.lang.set("eng")
        description2 = tk.Message(option_frame2, text="ex: kor/eng/jpn", aspect=1000)
        description2.grid(column=2, row=0)
        
        # audio file
        input_frame2 = tk.Frame(self.window, width=300, height=100)
        input_frame2.pack()
        label2 = tk.Label(input_frame2, text="오디오 파일 (*.wav)", width=25)
        label2.grid(column=0, row=0, padx=10, pady=5)
        textbox2 = tk.Entry(input_frame2, width=50, textvariable=self.selected_file2)
        textbox2.config(state="disabled")
        textbox2.grid(column=1, row=0, padx=10, pady=5)

        action2 = tk.Button(input_frame2, text="파일 선택", command=self.select_file2)
        action2.grid(column=2, row=0, padx=10, pady=5)
        
        # output
        output_frame = tk.Frame(self.window, width=300, height=100)
        output_frame.pack()
        out_label = tk.Label(output_frame, text="출력 디렉토리", width=25)
        out_label.grid(column=0, row=0, padx=10, pady=5)
        textbox = tk.Entry(output_frame, width=50, textvariable=self.output_fname)
        textbox.grid(column=1, row=0, padx=10, pady=5)
        

        action = tk.Button(output_frame, text="결과 추출", command=self.run)
        action.grid(column=2, row=0, padx=10, pady=5)
        

        status_frame = tk.Frame(self.window, width=300, height=100)
        status_frame.pack()
        label = tk.Label(status_frame, textvariable=self.status_text, width=300)
        label.pack()
        self.status_text.set("파일을 선택해주세요.")

    def run(self):
        if self.selected_file.get() == "":
            tk.messagebox.showinfo(title="알림", message="파일을 먼저 선택해주세요.")
            return

        text_file_path = self.selected_file.get()
        audio_file_path = self.selected_file2.get()
        output_file_path = self.output_fname.get()
        sheet_name = int(self.selected_sheet.get())
        lang = self.lang.get()
        if not os.path.exists(text_file_path):
            tk.messagebox.showinfo(title="알림", message="텍스트 파일이 존재하지 않습니다.")
            return
        if not os.path.exists(audio_file_path):
            tk.messagebox.showinfo(title="알림", message="오디오 파일이 존재하지 않습니다.")
            return
        if text_file_path.split(".")[-1] not in ["txt", "csv", "xlsx"]:
            tk.messagebox.showinfo(title="알림", message="적절한 파일 형식(*.txt, *.csv, *.xlsx)이 아닙니다.")
            return
        if audio_file_path.split(".")[-1] not in ["wav"]:
            tk.messagebox.showinfo(title="알림", message="적절한 파일 형식(*.wav)이 아닙니다.")
            return
        
        main_for_ui(
            text_filepath=text_file_path, 
            audio_filepath=audio_file_path, 
            outdir=output_file_path, 
            sheet_name=sheet_name,
            lang=lang
        )

    def select_file(self):
        loc = filedialog.askopenfilename()
        if not loc:
            self.selected_file.set("")
            self.status_text.set("텍스트 파일을 선택해주세요.")
            return
        self.selected_file.set(loc)

    def select_file2(self):
        loc2 = filedialog.askopenfilename()
        if not loc2:
            self.selected_file2.set("")
            self.status_text.set("오디오 파일을 선택해주세요.")        
        self.selected_file2.set(loc2)

        self.status_text.set("출력 디렉토리는 변경 가능합니다. 디렉토리 확인 후 결과 추출 버튼을 눌러주세요.")
        
        dirname = os.path.dirname(loc2)
        self.output_fname.set(os.path.join(dirname,"split_output"))

    def close(self):
        self.window.quit()
        self.window.destroy()