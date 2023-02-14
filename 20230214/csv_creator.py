import os
import pandas as pd

def create_csv(input_save_path, input_save_file_name, input_투약경로, input_처음투약양, input_유지투약양, input_환자_무게, input_유지투약_횟수, input_유지투약_간격시간, input_시간_간격, input_PMA_AMT):

    save_path = input_save_path.get()
    save_file_name = input_save_file_name.get()
    투약경로 = input_투약경로.get()

    처음투약양 = float(input_처음투약양.get())
    유지투약양 = float(input_유지투약양.get())
    환자_무게 = float(input_환자_무게.get())
    유지투약_횟수 = int(input_유지투약_횟수.get())
    유지투약_간격시간 = float(input_유지투약_간격시간.get())

    지정_시간1 = int(input_시간_간격.get().split(",")[0])
    지정_시간2 = int(input_시간_간격.get().split(",")[1])
    시간_간격1 = float(input_시간_간격.get().split(",")[2])
    시간_간격2 = float(input_시간_간격.get().split(",")[3])
    print(지정_시간1, 지정_시간2, 시간_간격1, 시간_간격2)

    PMA = float(input_PMA_AMT.get().split(",")[0])
    AMT_배수 = float(input_PMA_AMT.get().split(",")[1])

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

# a(input_save_path, input_save_file_name, input_투약경로, input_처음투약양, input_유지투약양, input_환자_무게, input_유지투약_횟수, input_유지투약_간격시간, input_시간_간격, input_PMA)
