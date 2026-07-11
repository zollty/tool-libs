import os
import pandas as pd
import sys

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

from music_analysis_and_processing.get_audio_info_mutagen import get_audio_info
from music_analysis_and_processing.normalize_loudness import normalize_loudness


# 从Excel文件读取响度数据
# 从Excel文件的所有sheet中读取响度数据
def read_loudness_data_from_all_sheets(filename):
    """
    从Excel文件的所有sheet中读取响度数据

    参数:
        filename (str): Excel文件名

    返回:
        dict: 以sheet名为键，响度值列表为值的字典
    """
    try:
        # 读取Excel文件中的所有sheet名称
        sheet_names = pd.ExcelFile(filename).sheet_names

        # 存储每个sheet的响度数据
        sheet_data = {}

        # 遍历每个sheet
        for sheet_name in sheet_names:
            # 读取特定sheet
            df = pd.read_excel(filename, sheet_name=sheet_name)

            # 检查是否存在"响度"列
            if "GAIN" in df.columns:
                gain_values = pd.to_numeric(df["GAIN"], errors='coerce').dropna().tolist()
                sheet_data[sheet_name] = {
                    "playlist": df["歌单"].tolist(),
                    "song_name": df["歌曲名"].tolist(),
                    "songer": df["歌手"].tolist(),
                    "gain_values": gain_values,
                }
            else:
                print(f"Sheet '{sheet_name}' 中未找到'响度'列")

        return sheet_data

    except FileNotFoundError:
        print(f"文件 {filename} 未找到")
        return {}
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return {}


if __name__ == "__main__":
    # arr = [-17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4]
    excel_file_path = "./output4.xlsx"
    # 从Excel文件的所有sheet读取响度数据
    all_sheet_data = read_loudness_data_from_all_sheets(excel_file_path)

    base_path = "/mnt/g/__SYNC4/music/"
    output_path = "/mnt/g/__SYNC4/output"

    if all_sheet_data:
        # 处理每个sheet的数据
        for sheet_name, obj in all_sheet_data.items():
            base_value = 0 - int(sheet_name.split("+")[1])
            print(f"\n{'=' * 50}")
            print(f"处理 Sheet: {sheet_name} 》》 base_value: {base_value}")
            print(f"{'=' * 50}")
            print("歌单:", obj["playlist"])
            print("歌曲名:", obj["song_name"])
            print("歌手:", obj["songer"])
            print("原始值列表:", obj["gain_values"])
            compensated_values = []
            for i, playlist_dir in enumerate(obj["playlist"]):
                # 处理文件名
                file_name = playlist_dir + "/" + str(obj["songer"][i]) + " - " + str(obj["song_name"][i])
                if os.path.isfile(base_path + file_name + ".flac"):
                    file_name += ".flac"
                elif os.path.isfile(base_path + file_name + ".mp3"):
                    file_name += ".mp3"
                else:
                    raise Exception(f"{file_name} 文件不存在!!")

                compensated_value = {
                    "path": file_name,
                    "gain_value": obj["gain_values"][i],
                }
                compensated_values.append(compensated_value)
                print(compensated_value)

                try:
                    file_full_path = base_path + file_name
                    output_full_path = output_path + "/" + playlist_dir

                    audio_info = get_audio_info(base_path + file_name, debug=False)

                    if abs(compensated_value["gain_value"]) < 0.1:
                        normalize_loudness(file_full_path, compensated_value["gain_value"], output_dir=output_full_path)
                    elif (audio_info['samplerate'] == 44100 and
                          (audio_info['subtype'] == 'MPEG_LAYER_III' or audio_info['subtype'] == 'PCM_16')):
                        continue
                    else:
                        normalize_loudness(file_full_path, compensated_value["gain_value"], output_dir=output_full_path)
                except Exception as e:
                    print(f"处理{file_name}时出错: {e}")
