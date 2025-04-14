# -*- coding: utf-8 -*-
import numpy as np
import argparse
import os
import json
import time
import multiprocessing
from tqdm.contrib.concurrent import process_map
import platform
import InziFormOcr as formOcr
import formOcr_test_util as test_util

parser = argparse.ArgumentParser(description="formOcr",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--image_dir', required=True, help='path to image_dir which contains text images')
parser.add_argument('-x', '--form_xml_path', required=True, type=str)
parser.add_argument('-m', '--form_ocr_mode', type=int, default="3")
parser.add_argument('-r', '--result_dir', type=str, default='result')
parser.add_argument('--time_log_file', type=str, default='_time_single.log')
parser.add_argument('--ocr_result_file', type=str, default='_ocr_single.log')
parser.add_argument('-c', '--cpu', type=int, default=0)
parser.add_argument('-s', '--num_sample', type=int, default=None)

args = parser.parse_args()

with open("./form_ocr_env.json", "r") as fp:
    env = json.load(fp)

if platform.system() == 'Windows':
    env = env['windows']
else:
    env = env['linux']

try:
    form_ocr = formOcr.IzFormOcr(env["dll_dir"])
except Exception as e:
    print(f'error: {str(e)}')
    exit()

form_ocr.set_env(env)


def form_ocr_multi(params):
    form_ocr_mode = params[0]
    form_file = params[1]
    img_file = params[2]
    return form_ocr.recog(form_ocr_mode, form_file, img_file)


def processTestCase(multi_process_count, testCase, maxSample, result_dir, time_log_file_path, ocr_result_file_path):
    process_sample_list = test_util.gen_sample_list (testCase, maxSample)
    data_count = len(process_sample_list)

    start = time.time()
    result_list = process_map(form_ocr_multi, process_sample_list, max_workers=multi_process_count, chunksize=1)
    elapsed = time.time() - start

    image_files = [result['img_file'] for result in result_list]
    times = np.array([result['elapsed'] for result in result_list])
    form_task_ids = [result['form_task_id'] for result in result_list]

    if result_dir:
        pass

    # test_util.log_time(time_log_file_path, times, elapsed, data_count, testCase["testName"])
    # test_util.log_ocr_result(ocr_result_file_path, result_list)
    test_util.save_text_image(result_dir, result_list)

    return data_count, image_files, times, form_task_ids, elapsed


def main():
    system_cpu_count = multiprocessing.cpu_count()
    used_cpu_count = int(system_cpu_count * 1)
    if args.cpu > 0:
        used_cpu_count = min (args.cpu, used_cpu_count)
    if args.num_sample == None:
        args.num_sample = 0
    if args.num_sample > 0:
        used_cpu_count = min (args.num_sample, used_cpu_count)

    test_util.print_env(system_cpu_count, used_cpu_count, args.num_sample, env['dll_dir'], env['model_dir'], env['ocr_data_dir'])
    print(f'- test info')
    print(f'  - image dir: {args.image_dir}')
    print(f'  - form xml: {args.form_xml_path}')
    print(f'  - ocr mode: {args.form_ocr_mode}')
    print(f'  - result dir: {args.result_dir}')
    print('--------------------------------------------------------')


    result_dir = args.result_dir
    os.makedirs(result_dir, exist_ok=True)

    time_log_file_path = os.path.join(result_dir, args.time_log_file)
    test_util.init_time_log_file(time_log_file_path, system_cpu_count, used_cpu_count)

    ocr_result_file_path = os.path.join(result_dir, args.ocr_result_file)
    test_util.init_ocr_result_file (ocr_result_file_path)

    case = {}
    case["testName"] = "single_test"
    case["data"] = [{"formFile": args.form_xml_path, "formOcrMode": args.form_ocr_mode, "imageDir": [args.image_dir]}]

    start = time.time()
    data_count, img_files, times, form_task_ids, total_time = processTestCase (
        used_cpu_count,
        case,
        args.num_sample,
        result_dir,
        time_log_file_path,
        ocr_result_file_path)
    case_times = []
    case_times.append(zip(img_files, times, form_task_ids))
    elapsed = time.time() - start
    # print('--------------------------------------------------------')
    print('-' * 100)
    print(f'Testing is done. {elapsed:0.3f} sec.')

    test_util.log_time_raw_data(time_log_file_path, elapsed, [case], case_times)


if __name__ == '__main__':
    main()
