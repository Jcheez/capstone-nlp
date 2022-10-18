from fileinput import filename
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showinfo
import os
import time

filechosen = [0]
application = [0]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        window_width = 800
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        paddings = {'padx': 5, 'pady': 5}

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.title('Application')

        # initialize data
        self.applications = ('Topic Modeling', 'Text Summarization', 'Social Media', 'Sentiment Analysis')

        # set up variable
        self.option_var = tk.StringVar(self)

        # create widget
        self.create_wigets()

        instructions_label = ttk.Label(text="Choose a txt file (.txt) for Text Summarization and Excel File (.xlsx) for all other Applications")
        instructions_label.grid(column=0,row=2, sticky=tk.W, **paddings)
        self.create_fileinput()

        self.file_chosen_label =  ttk.Label(text="File Chosen: ", foreground='red')
        self.file_chosen_label.grid(column=0, row=6, sticky=tk.W, **paddings)

        confirmation = ttk.Button(text="Confirm", command=self.close_app)
        # confirmation.grid(column=1, row=10, sticky=tk.W, **paddings)
        confirmation.place(relx=0.5, rely=0.8, anchor="center")


    def close_app(self):
        self.withdraw()
        self.destroy()


    def select_file(self):
        filetypes = (
            ('excel files', '*.xlsx'),
            ('All files', '*.*'),
            ('text files', "*.txt")
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='./assets/input',
            filetypes=filetypes)

        filechosen[0] = filename
        filename = os.path.basename(filename)
        self.file_chosen_label["text"] = f"File Chosen: {filename}"

    def create_fileinput(self):
        paddings = {'padx': 5, 'pady': 5}
        open_button = ttk.Button(self, text="Choose File", command=self.select_file)
        open_button.grid(column=0, row=4, sticky=tk.W)
        

    def create_wigets(self):
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}

        # label
        label = ttk.Label(self,  text='Which Application would you like to use:')
        label.grid(column=0, row=0, sticky=tk.W, **paddings)

        # option menu
        option_menu = ttk.OptionMenu(
            self,
            self.option_var,
            self.applications[0],
            *self.applications,
            command=self.option_changed)

        application[0] = self.applications[0]
        option_menu.grid(column=1, row=0, sticky=tk.W, **paddings)

        # output label
        self.output_label = ttk.Label(self, foreground='red')
        self.output_label.grid(column=0, row=1, sticky=tk.W, **paddings)

    def option_changed(self, *args):
        self.output_label['text'] = f'You selected: {self.option_var.get()}'
        application[0] = self.option_var.get()


if __name__ == "__main__":
    app = App()
    app.mainloop()
    
    if (filechosen[0] == 0 or application[0] == 0):
        print("No file or application chosen, application will now terminate")
        exit()
    
    if (application[0] == "Text Summarization"):
        if (".txt" not in filechosen[0]):
            print("Bad file type chosen for Text Summarization, please select a text file with .txt extension")
    
    if (application[0] != "Text Summarization"):
        if (".xlsx" not in filechosen[0]):
            print(f"Bad file type chosen for {application[0]}, please select an Excel file with extension .xlsx")
    
    print(f"{application[0]} for file {os.path.basename(filechosen[0])} will now be run")
    
    if (application[0] == "Topic Modeling"):
        from topicModelling import topic_model
        topic_model(filechosen[0])
    # elif (application[0] == "Text Summarization"):
    #     run_summary
    # elif (application[0] == "Social Media"):
    #     run_social
    # elif (application[0] == "Sentiment Analysis"):
    #     run_senti




