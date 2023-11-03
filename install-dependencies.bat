@echo off
color 1f
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Welcome to the dependencies installer.
echo.
echo. Please note that:
echo. 1. You will need Python installed to run
echo.    the dependencies installer.
echo. 2. If it doesn't work for you, try the second method in readme.
echo.
echo. If you do not want to install the dependencies, press Ctrl+C.
echo. If you do want to install the dependencies, press any key.
pause >nul
echo.
echo. Good - installing!
echo. Press any key to continue...
pause >nul
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Change dir to C:\Program Files\Python311\Scripts [1/9]
cd C:\Program Files\Python311\Scripts
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install pygame --pre [2/9]
pip3 install pygame --pre
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install mutagen [3/9]
pip3 install mutagen
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install easing-functions [4/9]
pip3 install easing-functions
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install pywin32 [5/9]
pip3 install pywin32
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install pyautogui [6/9]
pip3 install pyautogui
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install pypresence [7/9]
pip3 install pypresence
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Run pip3 install numpy [8/9]
pip3 install numpy
cls
echo. Install GDR dependencies
echo ---------------------------------
echo. Change dir to %userprofile%\Downloads [9/9]
cd %userprofile%\Downloads
echo. Done!
echo. Press any key to quit.
pause >nul
color
exit
