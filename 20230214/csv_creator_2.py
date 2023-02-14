import os
import pandas as pd
import argparse
import json
import numpy as np

def create_csv(input_save_path, input_save_file_name, input_투약경로, input_처음투약양, input_유지투약양, input_환자_무게, input_유지투약_횟수, input_유지투약_간격시간, input_시간_간격, input_PMA_AMT):

    save_path = input_save_path
    save_file_name = input_save_file_name
    투약경로 = input_투약경로

    처음투약양 = float(input_처음투약양)
    유지투약양 = float(input_유지투약양)
    환자_무게 = float(input_환자_무게)
    유지투약_횟수 = int(input_유지투약_횟수)
    유지투약_간격시간 = float(input_유지투약_간격시간)

    지정_시간1 = int(input_시간_간격.split(",")[0])
    지정_시간2 = int(input_시간_간격.split(",")[1])
    시간_간격1 = float(input_시간_간격.split(",")[2])
    시간_간격2 = float(input_시간_간격.split(",")[3])
    print(지정_시간1, 지정_시간2, 시간_간격1, 시간_간격2)

    PMA = float(input_PMA_AMT.split(",")[0])
    AMT_배수 = float(input_PMA_AMT.split(",")[1])

    save_path = os.path.join(save_path, save_file_name) + ".csv"
    총_처음_투약량 = 처음투약양 * 환자_무게
    총_유지_투약량 = 유지투약양 * 환자_무게

    iv_col_list = ["ID", "TIME", "AMT", 'RATE', "DV", "MDV", "CMT", "WT", "PMA"]
    oral_col_list = ["ID", "TIME", "AMT", "DV", "MDV", "CMT", "WT", "PMA"]

    if 투약경로.upper()=="IV":
        data_list = []
        before_data = []
        for ID in range(1, 1001):
            for TIME in range(int(지정_시간1/시간_간격1)+1):
                TIME  = TIME*시간_간격1
                if TIME>지정_시간1:
                    break
                AMT = "."
                RATE  = "."
                DV = 0
                MDV = 0
                CMT = 2
                WT = 환자_무게
                PMA = PMA
                if TIME==0:
                    AMT=총_처음_투약량
                    MDV=1
                    DV="."
                    RATE=AMT*AMT_배수
                elif TIME%유지투약_간격시간==0:
                    data_list.append([ID, TIME, ".", ".", ] + before_data[4:])
                    AMT=총_유지_투약량/유지투약_횟수
                    MDV=1
                    DV="."
                    RATE=AMT*AMT_배수
                data = [ID, TIME, AMT, RATE, DV, MDV, CMT, WT, PMA]
                before_data = data
                data_list.append(data)

            for TIME in range(int(지정_시간2/시간_간격2)+1):
                TIME  = TIME*시간_간격2
                if TIME<=지정_시간1:
                    continue
                elif TIME>지정_시간2:
                    break
                AMT = "."
                RATE  = "."
                DV = 0
                MDV = 0
                CMT = 2
                WT = 환자_무게
                PMA = PMA
                if TIME==0:
                    AMT=총_처음_투약량
                    MDV=1
                    DV="."
                    RATE=AMT*AMT_배수
                elif TIME%유지투약_간격시간==0:
                    data_list.append([ID, TIME, ".", ".", ] + before_data[4:])
                    AMT=총_유지_투약량/유지투약_횟수
                    MDV=1
                    DV="."
                    RATE=AMT*AMT_배수
                data = [ID, TIME, AMT, RATE, DV, MDV, CMT, WT, PMA]
                before_data = data
                data_list.append(data)

        df = pd.DataFrame(data_list, columns=iv_col_list)
        df.to_csv(save_path, index=False)


    elif 투약경로.upper()=="ORAL":
        data_list = []
        before_data = []
        for ID in range(1, 1001):
            for TIME in range(int(지정_시간1/시간_간격1)+1):
                TIME  = TIME*시간_간격1
                if TIME>지정_시간1:
                    break
                AMT = "."
                RATE  = "."
                DV = 0
                MDV = 0
                CMT = 2
                WT = 환자_무게
                PMA = PMA
                if TIME==0:
                    AMT=총_처음_투약량
                    MDV=1
                    CMT=1
                    DV="."
                    RATE=0
                elif TIME%유지투약_간격시간==0 and 유지투약_횟수:
                    data_list.append([ID, TIME, ".", ] + before_data[3:])
                    AMT=총_유지_투약량/유지투약_횟수
                    MDV=1
                    CMT=1
                    DV="."
                    RATE=0
                data = [ID, TIME, AMT, DV, MDV, CMT, WT, PMA]
                before_data = data
                data_list.append(data)

            for TIME in range(int(지정_시간2/시간_간격2)+1):
                TIME  = TIME*시간_간격2
                if TIME<=지정_시간1:
                    continue
                elif TIME>지정_시간2:
                    break
                AMT = "."
                RATE  = "."
                DV = 0
                MDV = 0
                CMT = 2
                WT = 환자_무게
                PMA = PMA
                if TIME==0:
                    AMT=총_처음_투약량
                    MDV=1
                    CMT=1
                    DV="."
                    RATE=0
                elif TIME%유지투약_간격시간==0 and 유지투약_횟수:
                    data_list.append([ID, TIME, ".", ] + before_data[3:])
                    AMT=총_유지_투약량/유지투약_횟수
                    MDV=1
                    CMT=1
                    DV="."
                    RATE=0
                data = [ID, TIME, AMT, DV, MDV, CMT, WT, PMA]
                before_data = data
                data_list.append(data)

        df = pd.DataFrame(data_list, columns=oral_col_list)
        df.to_csv(save_path, index=False)


def create_directory_if_not_exists(directory):
    # directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', type=str, default="input.json", help='input json file')
    args = parser.parse_args()

    with open(args.input_json, 'r', encoding="utf-8") as f:
        input = json.load(f)
    print(input)

    input_save_path = input["파일저장경로"]
    input_save_file_name = input["파일명"]
    input_투약경로 = input["투약경로"]
    input_처음투약양 = input["처음투약양"]
    input_유지투약양 = input["유지투약양"]
    input_환자_무게 = input["환자Weight"]
    input_유지투약_횟수 = input["유지투약횟수"]
    input_유지투약_간격시간 = input["유지투약간격시간"]
    input_시간_간격 = input["시간1_2_간격1_2"]
    input_PMA_AMT = input["환자PMA_AMT배수"]

    input_유지투약양_range = list(map(float, input_유지투약양.split("-")))
    PMA_AMT = input_PMA_AMT.split(",")
    PMA = PMA_AMT[0]
    AMT = PMA_AMT[1]
    PMA_range = list(map(float, PMA.split("-")))

    create_directory_if_not_exists(input_save_path)

    if len(input_유지투약양_range) == 3:

        file_name = int(input_save_file_name)
        for 유지투약양 in np.arange(input_유지투약양_range[0], input_유지투약양_range[1], input_유지투약양_range[2]):

            create_csv(
                input_save_path,
                str(file_name),
                input_투약경로,
                input_처음투약양,
                유지투약양,
                input_환자_무게,
                input_유지투약_횟수,
                input_유지투약_간격시간,
                input_시간_간격,
                input_PMA_AMT)

            file_name += 1

    elif len(PMA_range) == 3:

        file_name = int(input_save_file_name)
        for PMA in np.arange(PMA_range[0], PMA_range[1], PMA_range[2]):

            sub_input_PMA_AMT = str(PMA) + "," + str(AMT)
            create_csv(
                input_save_path,
                str(file_name),
                input_투약경로,
                input_처음투약양,
                input_유지투약양,
                input_환자_무게,
                input_유지투약_횟수,
                input_유지투약_간격시간,
                input_시간_간격,
                sub_input_PMA_AMT)

            file_name += 1

    else:

        create_csv(
            input_save_path,
            input_save_file_name,
            input_투약경로,
            input_처음투약양,
            input_유지투약양,
            input_환자_무게,
            input_유지투약_횟수,
            input_유지투약_간격시간,
            input_시간_간격,
            input_PMA_AMT)
