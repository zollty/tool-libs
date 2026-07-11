import os, shutil

# 指定文件夹路径
out_folder_path = 'H:/__00-DEVICE_SHARE/out'  # 替换为你的文件夹路径

pics = []
# 获取文件夹中的所有文件
for filename in os.listdir(out_folder_path):
    # 打印新的文件名
    print(filename)
    pics.append(filename)

idx = 0


folders = ["H1-Exuberant", "H2-Joyful", "H3-Mellow", "R4-Relaxed", "S0-Serene", "S3-Gentle",
           "V1-Energetic", "V2-Vibrant", "V3-Moderate"]

# 指定文件夹路径
folder_path = 'I:/10-MUSIC/'  # 替换为你的文件夹路径

for folder in folders:
    folder_path = 'I:/10-MUSIC/' + folder
    # 获取文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 分离文件名和扩展名
        name, ext = os.path.splitext(filename)
        # 修改扩展名为.jpg
        new_filename = name + '.jpg'
        # 打印新的文件名
        print(new_filename)

        if idx >= len(pics):
            idx = 0
        pic_file = pics[idx]
        idx += 1
        # os.rename(os.path.join(out_folder_path, pic_file), os.path.join(folder_path, new_filename))
        shutil.copy2(os.path.join(out_folder_path, pic_file), os.path.join(folder_path, new_filename))


