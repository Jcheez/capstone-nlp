## Installation Guide

### Windows Installation
1. Install Visual Studio C++ build tools
https://stackoverflow.com/questions/64261546/how-to-solve-error-microsoft-visual-c-14-0-or-greater-is-required-when-inst

2. Install [python](https://www.python.org/downloads/)

3. Download [vusual studio Code](https://code.visualstudio.com/download)

4. Download the project by clicking Code -> Download Zip. Unzip the project and place the unzipped folder in the desktop.

5. Open up Visual Studio Code. Click on File -> Open Folder. Open up the project from the desktop

6. In visual studio code, click Terminal -> New Terminal. Type the following code in the terminal: `pip install virtualenv`

5. Create a new virtual environment using the following code: `virtualenv venv`

6. Start virtual environemnt (venv) using: `venv\Scripts\activate`

7. Install requirements: `pip install -r requirements.txt`

8. Type the following code: `python main.py`