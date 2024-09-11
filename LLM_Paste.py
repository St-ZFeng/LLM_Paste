import pyperclip
import time
import keyboard
import openai
import json
from openai import OpenAI
import tkinter as tk
from tkinter import ttk

import pytgpt.auto as auto
from pytgpt.imager import Prodia
from PIL import Image
import win32clipboard
import win32clipboard as clip
from io import BytesIO
import asyncio

def setImage(data):
    clip.OpenClipboard() #打开剪贴板
    clip.EmptyClipboard()  #先清空剪贴板
    clip.SetClipboardData(win32clipboard.CF_DIB, data)  #将图片放入剪贴板
    clip.CloseClipboard()

def send_LLM(text,prompt,textg,loop):
    asyncio.set_event_loop(loop)
    openai_p=use_openai.get()
    openai.api_key = API_key
    openai.api_base = Url+"/v1"
    client = OpenAI(
        api_key=API_key,
        base_url=Url,
    # This is the default and can be omitted
          
    )

    try:
        if textg:
            if openai_p:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt+". The text you need to process this time is as follows:\n"+text+"\nYou are now a competent and reliable machine, not a conscious agent. So you just complete the task operation, return clean result text, and don't add anything else.",
                        }
                    ],
                    model=model,timeout=60)
                
                print(chat_completion.choices[0].message.content)
                res=chat_completion.choices[0].message.content
            else:
                bot = auto.AUTO()
                res=bot.chat(prompt+". The text you cannot identify image file <_io.BytesIO object at 0x000001758DD6E430> to process this time is as follows:\n"+text+"\nYou are now a competent and reliable machine, not a conscious agent. So you just complete the task operation, return clean result text, and don't add anything else.")
            pyperclip.copy(res)
        else:
            img = Prodia()
            generated_images = img.generate(prompt=prompt+"\n"+text, amount=1)
            pic=generated_images[0]
            
            if b'500: Internal Server Error' == pic:
                pyperclip.copy("Internet Server Error")
                return None
            image = Image.open(BytesIO(pic))
            output=BytesIO()
            image.save(output, "BMP") #以RGB模式保存图像
            data = output.getvalue()[14:]
            output.close()
            setImage(data)
                    
        
    except Exception as e:
        print(str(e))
        pyperclip.copy(str(e))
    return None
    
    #return chat_completion.choices[0].message.content
def read_config():
    # 读取setting.json中的model，URL，api，和model_select列表
    with open('setting.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    
    model = config.get('model')
    Url = config.get('Url')
    API_key = config.get('API_key')
    model_select = config.get('model_select')
    
    return model, Url, API_key, model_select
def write_config(new_settings):
    # 读取现有的setting.json文件
    try:
        with open('setting.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {}

    # 更新配置
    config.update(new_settings)

    # 将更新后的配置写回setting.json文件
    with open('setting.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)    

def load_prompt():
    #读取json文件
    with open('prompts.json', 'r') as f:
        prompt_list = json.load(f)
    return prompt_list

def on_copy_event():
    task=selected_task.get()
    #根据任务名获取对应的prompt
    prompt=[n["prompt"] for n in tasks if n["task"]==task]
    textg=[n["text_g"] for n in tasks if n["task"]==task]
    if len(prompt)>0:
    #global last_clipboard_content
    # 获取当前剪贴板内容
        progress.start()
        time.sleep(0.1)
        current_clipboard_content = pyperclip.paste()
        # 如果剪贴板内容和上次不同，则认为有文本被选中
        #if current_clipboard_content != last_clipboard_content:
        #last_clipboard_content = current_clipboard_content
        print(current_clipboard_content)
        send_LLM_thread(current_clipboard_content,prompt[0],textg[0])
        progress.stop()
    return None
    #return None

def send_LLM_thread(text,prompt,textg):
    loop = asyncio.new_event_loop()
    import threading
    t = threading.Thread(target=send_LLM, args=(text,prompt,textg,loop,))
    t.start()
    t.join()



if __name__ == "__main__":
    model, Url, API_key, model_select=read_config()
    #检测是否有prompt.json文件，没有则创建
    try:
        with open('prompts.json', 'r') as f:
            pass
    except FileNotFoundError:
        with open('prompts.json', 'w') as f:
            json.dump([], f, indent=4)
    tasks = load_prompt()
    #读取任务列表，如果任务为空，自动添加
    if len(tasks)==0:
        tasks.append(
            {
                "task": "Translate to English",
                "prompt": "You are a English translate expert and your job is to translate text to English.",
                "text_g":False
            }
        )
        #保存到json文件


    with open('prompts.json', 'w') as f:
        json.dump(tasks, f, indent=4)
    tasknames = [n["task"] for n in tasks]

    # 创建主窗口
    root = tk.Tk()
    root.title("LLM Paste")

    # 固定窗口大小
    root.geometry("700x200")
    window_width = 700
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    # 创建主框架
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 创建一个标签显示“Select Task”
    label = ttk.Label(frame, text="Select Task", font=("Arial", 14))
    label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    # 创建一个变量来存储选择结果
    selected_task = tk.StringVar(value="")
    #创建一个复选框，存储是否采用openai
    use_openai=tk.BooleanVar(value=True)
    use_openai_cb = ttk.Checkbutton(frame, text="Use OpenAI", variable=use_openai)
    use_openai_cb.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    

    # 创建任务选择框的容器，并添加滚动条
    canvas = tk.Canvas(frame, width=300, height=60)


    # 将 canvas 放置在框架的左侧，占用三行
    canvas.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E),rowspan=2,columnspan=2)

    # 创建一个内部框架来放置任务选择按钮
    task_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=task_frame, anchor="nw")

    # 更新滚动区域
    def update_scrollregion(event=None):
        canvas.config(scrollregion=canvas.bbox("all"))

    task_frame.bind("<Configure>", update_scrollregion)

    # 绑定鼠标滚轮事件
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows 和 Mac 适用
    canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux 适用
    canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux 适用

    # 创建并显示任务选择框
    for task in tasknames:
        rb = ttk.Radiobutton(task_frame, text=task, variable=selected_task, value=task)
        rb.pack(anchor=tk.W, padx=5, pady=5)

    # 创建“清空”按钮
    def clear_selection():
        selected_task.set(None)

    clear_button = ttk.Button(frame, text="Clear", command=clear_selection)
    clear_button.grid(row=3, column=0, sticky=tk.W, padx=30, pady=10)
    #创建”删除“按钮
    def delete_task():
        task = selected_task.get()
        for n in tasks:
            if n["task"]==task:
                tasks.remove(n)
                break
        tasknames.remove(task)
        for widget in task_frame.winfo_children():
            widget.destroy()
        for task in tasknames:
            rb = ttk.Radiobutton(task_frame, text=task, variable=selected_task, value=task)
            rb.pack(anchor=tk.W, padx=5, pady=5)
        update_scrollregion()
        #保存到json文件
        with open('prompts.json', 'w') as f:
            json.dump(tasks, f, indent=4)
            
    # 创建一个标签，显示"Add Task",在selected_task右侧
    label = ttk.Label(frame, text="Add Task", font=("Arial", 14))
    label.grid(row=0, column=2, sticky=tk.W, padx=30, pady=5, columnspan=2)

    # 创建任务添加的容器，包括任务名和prompt两个字段及其输入框
    task_name = tk.StringVar()
    prompt = tk.StringVar()
    # 创建任务名:标签
    label = ttk.Label(frame, text="Task Name:")
    label.grid(row=1, column=2, sticky=tk.W, padx=30, pady=5)

    # 创建任务名输入框
    task_name_entry = ttk.Entry(frame, textvariable=task_name)
    task_name_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
    # 创建prompt:标签
    label = ttk.Label(frame, text="Prompt:")
    label.grid(row=2, column=2, sticky=tk.W, padx=30, pady=5)

    # 创建prompt多行输入框
    prompt_entry = ttk.Entry(frame, textvariable=prompt)
    prompt_entry.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)

    # 创建“添加”按钮
    def add_task():
        task = task_name.get()
        prompt_text = prompt.get()
        if task and prompt_text:
            tasks.append({"task": task, "prompt": prompt_text})
            tasknames.append(task)
            rb = ttk.Radiobutton(task_frame, text=task, variable=selected_task, value=task)
            rb.pack(anchor=tk.W, padx=5, pady=5)
            task_name.set("")
            prompt.set("")
            update_scrollregion()
            #保存到json文件
            with open('prompts.json', 'w') as f:
                json.dump(tasks, f, indent=4)



    add_button = ttk.Button(frame, text="Add", command=add_task)
    add_button.grid(row=3, column=2, sticky=tk.W, padx=50, pady=5)


    # 创建“删除”按钮
    delete_button = ttk.Button(frame, text="Delete", command=delete_task)
    delete_button.grid(row=3, column=3, sticky=tk.W, padx=30, pady=5)

    def process_API():
        global API_key
        global Url
        global model
        
        #弹出对话框，提供模型选择，API key输入，URL输入
        subroot = tk.Tk()
        subroot.title("API Setting")
        subroot.geometry("300x200")
        # 控制弹出位置在屏幕中央
        window_width = 300
        window_height = 200
        screen_width = subroot.winfo_screenwidth()
        screen_height = subroot.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        subroot.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        # 创建主框架
        frame = ttk.Frame(subroot, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 创建一个标签显示“Select Model”
        label = ttk.Label(frame, text="Model", font=("Arial", 14))
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        # 创建一个变量来存储选择结果
        selected_model = tk.StringVar(value=model)
        # 下拉框
        model_combobox = ttk.Combobox(frame, textvariable=selected_model, values=model_select)
        model_combobox.set(model)
        model_combobox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        # 创建一个标签显示“API Key”
        label = ttk.Label(frame, text="API Key", font=("Arial", 14))
        label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        # 创建API Key输入框
        Api_key = tk.StringVar()
        
        API_key_entry = ttk.Entry(frame, textvariable=Api_key,show="*",width=22)
        API_key_entry.insert(0, API_key)
        API_key_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        # 创建一个标签显示“URL”
        label = ttk.Label(frame, text="URL", font=("Arial", 14))
        label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        # 创建URL输入框
        URL = tk.StringVar()
        URL_entry = ttk.Entry(frame, textvariable=URL,width=22)
        URL_entry.insert(0, Url)
        URL_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        # 创建“保存”按钮
        def save_setting():
            global API_key
            global Url
            global model
            API_key = API_key_entry.get()
            Url = URL_entry.get()
            model=model_combobox.get()
            new_cif={"API_key":API_key,"Url":Url,"model":model}
            write_config(new_cif)
            subroot.destroy()
        save_button = ttk.Button(frame, text="Save", command=save_setting)
        save_button.grid(row=3, column=1, sticky=tk.W, padx=5, pady=25)



        
    #
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # 创建文件菜单
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Setting", menu=file_menu)
    file_menu.add_command(label="API", command=process_API)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit)

    # 创建进度条控件
    progress = ttk.Progressbar(root, mode='determinate', length=80)
    progress.grid(row=0, column=0, sticky=tk.W, padx=200, pady=134)
    keyboard.add_hotkey('ctrl+c', on_copy_event)

    # 运行主窗口
    root.mainloop()


#打包exe文件，无cmd窗口，排除numpy和pandas
#pyinstaller -F -w LLM_Paste.py  --exclude-module numpy  --exclude-module pandas
