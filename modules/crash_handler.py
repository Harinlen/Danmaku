# -*- coding: utf-8 -*-
import asyncio
import sys
import traceback
import tkinter
import tkinter.messagebox


def show_crash_report():
    root = tkinter.Tk()
    root.title('错误报告')
    root.resizable(0, 0)
    # Create frame.
    frame = tkinter.Frame(root)
    frame.grid(row=3, column=0)

    tkinter.Label(frame, text="服务器运行产生异常").grid(row=1, column=0)
    tkinter.Label(frame, text="我们很抱歉服务器崩溃了，请联系开发者并将如下信息提供给开发者。").grid(row=2, column=0)
    crash_stack = tkinter.Text(frame)
    crash_stack.grid(row=3, column=0)
    crash_stack.insert(tkinter.END, traceback.format_exc())

    root.eval('tk::PlaceWindow . center')
    root.mainloop()
    # Stop the server execution
    loop = asyncio.get_running_loop()
    loop.stop()
    sys.exit(-1)


def show_error(title: str, message: str) -> None:
    tkinter.messagebox.showerror(title, message)
