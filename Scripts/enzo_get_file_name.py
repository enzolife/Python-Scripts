import os
import pandas as pd

data = []
print(os.getcwd())
os.chdir("D:\Program Files (x86)\\百度云同步盘\\Dropbox\\-E·J- 2014.5.1\\"
         "2016.9.22 千娇子\\2017.10.18 小富兰克抓取数据\\20171018-XIAOFULANKE-IMAGES")

folder_path = os.getcwd()

for folder in sorted(os.listdir(folder_path)):
    sub_folder_path = os.path.join(folder_path, folder)
    for sub_folder in sorted(os.listdir(sub_folder_path)):
        file_path = os.path.join(folder_path, folder, sub_folder)
        i = 1
        for file in sorted(os.listdir(file_path)):
            data.append((folder, sub_folder, i, file))
            i = i + 1

df = pd.DataFrame(data, columns=['Folder', 'Sub-folder', 'Num', 'File'])
df.to_csv(os.getcwd() + '\\商品图片路径.csv', sep=',')
