# -*- coding: utf-8 -*-
from ctypes import *
import cv2
import os
import json
import time
import platform
import numpy as np


class IzFormOcr:

    IZ_FORM_CONF_CONFIG_FILEPATH          = 1  # 환경설정 정보 xml 파일명
    IZ_FORM_CONF_FORM_FILEPATH            = 2  # 서식정보파일명(비정형)
    IZ_FORM_CONF_MODEL_DIRECTORY          = 3  # 인식모델 디렉토리
    IZ_FORM_CONF_OCR_DATA_DIRECTORY       = 4  # ocrData 디렉토리
    IZ_FORM_CONF_PROCESS_MODE             = 5  # 처리모드
    IZ_FORM_CONF_IMAGE_ORIENTATION        = 6  #입력 이미지의 회전된 각도
    IZ_FORM_CONF_NUM_THREAD               = 7  # 병렬처리시 스레드 개수
    IZ_FORM_CONF_SKEW_CORRECTION          = 8  # skew 보정 수행유무
    IZ_FORM_CONF_REDUCE_IMAGE_SIZE        = 9  # 이미지 축소 해상도 (단위: pixel)
    IZ_FORM_CONF_RECOG_LANG_TYPE          = 10 # 인식언어타입
    IZ_FORM_CONF_TE_DOC_TYPE              = 11 # [텍스트라인 추출] 문서 타입
    IZ_FORM_CONF_TE_DOC_SUB_TYPE          = 12 # [텍스트라인 추출] 문서특성 옵션 (세부처리 옵션)
    IZ_FORM_CONF_TE_REDUCERATIO16         = 13 # [텍스트라인 추출] 축소 비율 (0 ~ 16)
    IZ_FORM_CONF_TE_INVERSE_TYPE          = 14 # [텍스트라인 추출] 역상처리 방식
    IZ_FORM_CONF_RESULT_STR_ENCODING      = 15 # 인식결과 문자열 인코딩
    IZ_FORM_CONF_SIZE_OF_WCHAR            = 16 # 인식결과 문자의 wchar_t size
    IZ_FORM_CONF_RESULT_ENDIAN_TYPE       = 17 # 인식결과 문자열 endian type
    IZ_FORM_CONF_LOG_VERBOSITY            = 18 # 로그 상세출력 설정
    IZ_FORM_CONF_GLOBAL_LOG_DIRECTORY     = 19 # 모듈의 모든 로그 저장 디렉토리
    IZ_FORM_CONF_INPUT_IMAGE_LOG_FILEPATH = 20 # 모듈 입력 이미지로그 파일경로
    IZ_FORM_CONF_PROGRESS_LOG_FILEPATH    = 21 # 프로그레스 로그 파일경로
    IZ_FORM_CONF_PROGRESS_LOG_OVERWRITE   = 22 # 신규 로그를 저장할 때 기존내용을 삭제할지 유무
    IZ_FORM_CONF_PROGRESS_LOG_MAX_SIZE    = 23 # 로그파일 최대 크기(byte)
    IZ_FORM_CONF_AUTOCROP_OBJECT_TYPE     = 24 # AutoCrop 옵션: 대상 물체 타입 지정
    IZ_FORM_CONF_AUTOCROP_INSIDE_BOUND    = 25 # AutoCrop 옵션: 반드시 포함되어야 할 영역 지정
    IZ_FORM_CONF_EXECUTE_FORM_ID          = 26 # 수행할 서식의 form id를 지정. 지정된 서식만 처리

    IZ_FORM_SUB_ITEM_FORM_ID              =	1  # 서식 ID
    IZ_FORM_SUB_ITEM_FORM_NAME            =	2  # 서식 이름
    IZ_FORM_SUB_ITEM_MULTI_BLOCK          = 3  # 결과에 여러블록 출력 유무
    IZ_FORM_SUB_ITEM_PAGE_INDEX           =	4  # 페이지 인덱스
    IZ_FORM_SUB_ITEM_FIELD_ID             =	5  # 필드 ID
    IZ_FORM_SUB_ITEM_FIELD_NAME           =	6  # 필드 이름
    IZ_FORM_SUB_ITEM_FIELD_SECURITY       = 7  # 필드 보안유무
    IZ_FORM_SUB_ITEM_FIELD_CATEGORY       = 8  # 필드 카테고리 id
    IZ_FORM_SUB_ITEM_RECOG_STRING         = 9  # 인식된 문자열
    IZ_FORM_SUB_ITEM_REGION               = 10 # 인식된 영역
    IZ_FORM_SUB_ITEM_SCORE                = 11 # 정확도 점수
    IZ_FORM_SUB_ITEM_WORD_OBJ             = 12 # word 정보 객체

    # conf_priority =
    model_dir = "./data/model/"
    ocr_data_dir = "./data/ocrdata/"
    conf_path = ""
    log_verbosity = 0
    log_dir = ""


    def __init__(self, dll_dir="./") -> None:
        try:
            self.dll_name = os.path.join(dll_dir, "libInziFormOcr")
            if platform.system() == 'Windows':
                self.dll_name += ".dll"
            else:
                self.dll_name += ".so"
            # print(f"dll_path: {self.dll_name}")
            self.load_lib(dll_name=self.dll_name)
            self.bind_func(self.form_ocr_dll)
        except Exception as e:
            raise


    def __del__(self):
        pass


    def load_lib(self, dll_name):
        if platform.system() == 'Windows':
            self.form_ocr_dll = WinDLL(dll_name)
        else:
            self.form_ocr_dll = CDLL(dll_name)


    def bind_func(self, form_ocr_dll):

        self.IZ_form_getVersion = form_ocr_dll['IZ_form_getVersion']
        self.IZ_form_getVersion.restype = c_char_p

        self.IZ_form_getFormXmlVersion = form_ocr_dll['IZ_form_getFormXmlVersion']
        self.IZ_form_getFormXmlVersion.restype = c_char_p

        self.IZ_form_getErrorMessage = form_ocr_dll['IZ_form_getErrorMessage']
        self.IZ_form_getErrorMessage.argtypes = [c_int]
        self.IZ_form_getErrorMessage.restype = c_char_p

        self.IZ_form_createFormParam = form_ocr_dll['IZ_form_createFormParam']
        self.IZ_form_createFormParam.argtypes = [POINTER(c_int)]
        self.IZ_form_createFormParam.restype = c_void_p

        self.IZ_form_destroyFormParam = form_ocr_dll['IZ_form_destroyFormParam']
        self.IZ_form_destroyFormParam.argtypes = [POINTER(c_void_p)]

        self.IZ_form_setConfigurations = form_ocr_dll['IZ_form_setConfigurations']
        self.IZ_form_setConfigurations.argtypes = [c_void_p, c_int, c_char_p]
        self.IZ_form_setConfigurations.restype = c_int

        self.IZ_form_getConfigurations = form_ocr_dll['IZ_form_getConfigurations']

        self.IZ_form_setRoi = form_ocr_dll['IZ_form_setRoi']
        self.IZ_form_setRoi.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
        self.IZ_form_setRoi.restype = c_int

        self.IZ_form_setImage = form_ocr_dll['IZ_form_setImage']
        self.IZ_form_initIzFormResult = form_ocr_dll['IZ_form_initIzFormResult']
        self.IZ_form_processRecognition = form_ocr_dll['IZ_form_processRecognition']
        self.IZ_form_analyzeDocumentSet = form_ocr_dll['IZ_form_analyzeDocumentSet']
        self.IZ_form_freeIzFormResult = form_ocr_dll['IZ_form_freeIzFormResult']

        self.IZ_form_getResultJson = form_ocr_dll['IZ_form_getResultJson']

        self.IZ_form_getDocumentCount = form_ocr_dll['IZ_form_getDocumentCount']
        self.IZ_form_getDocumentPageCount = form_ocr_dll['IZ_form_getDocumentPageCount']
        self.IZ_form_getImageIndex = form_ocr_dll['IZ_form_getImageIndex']
        self.IZ_form_getFormInfo = form_ocr_dll['IZ_form_getFormInfo']
        self.IZ_form_getDefinedFieldCount = form_ocr_dll['IZ_form_getDefinedFieldCount']
        self.IZ_form_getDefinedFieldInfo = form_ocr_dll['IZ_form_getDefinedFieldInfo']
        self.IZ_form_getBlockCount = form_ocr_dll['IZ_form_getBlockCount']
        self.IZ_form_getBlockId = form_ocr_dll['IZ_form_getBlockId']
        self.IZ_form_getBlockAttribute = form_ocr_dll['IZ_form_getBlockAttribute']
        self.IZ_form_getBlockFieldCount = form_ocr_dll['IZ_form_getBlockFieldCount']
        self.IZ_form_getBlockFieldResult = form_ocr_dll['IZ_form_getBlockFieldResult']
        self.IZ_form_getFieldWordCount = form_ocr_dll['IZ_form_getFieldWordCount']
        self.IZ_form_getFieldWordResult = form_ocr_dll['IZ_form_getFieldWordResult']
        self.IZ_form_getResultJson = form_ocr_dll['IZ_form_getResultJson']


    def set_env(self, env):
        self.model_dir = env["model_dir"]
        self.ocr_data_dir = env["ocr_data_dir"]
        self.log_verbosity = env["log_verbosity"]
        self.log_dir = env["log_dir"]


    def print_err (self, ec):
        errmsg = self.IZ_form_getErrorMessage(ec)
        errmsg =str(errmsg,'utf-8')
        print("error - [" + str(ec) + "] " + errmsg)


    def set_conf (self, fp_ptr, conf_type, value):
        # 엔진에서 한글파일명 읽어올 수 있도록 적절한 endocing 설정
        if platform.system() == 'Windows':
            encoding = "euckr"
        else:
            encoding = "utf-8"
        return self.IZ_form_setConfigurations (fp_ptr, conf_type, bytes(value, encoding=encoding))


    def set_required_conf (self, fp_ptr):
        # conf 파일이 있으면 우선 적용함.
        # conf 파일에는 반드시 model_dir, ocr data dir이 설정되어 있어야 함.
        if len(self.conf_path) > 0:
            ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_CONFIG_FILEPATH, self.conf_path)
            if ec != 0:
                return ec

            szBuffer = 511
            conf_value = create_string_buffer(szBuffer)
            ec = self.IZ_form_getConfigurations(fp_ptr, self.IZ_FORM_CONF_MODEL_DIRECTORY, conf_value)
            if ec != 0:
                return ec
            if conf_value is None:
                return -1
            conf_value = conf_value.value.decode()
            # print(f"model dir: {conf_value}")
            if len(conf_value) <= 0:
                ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_MODEL_DIRECTORY, self.model_dir)
                if ec != 0:
                    return ec

            conf_value = create_string_buffer(szBuffer)
            ec = self.IZ_form_getConfigurations(fp_ptr, self.IZ_FORM_CONF_OCR_DATA_DIRECTORY, conf_value)
            if ec != 0:
                return ec
            if conf_value is None:
                return -1
            conf_value = conf_value.value.decode()
            # print(f"ocr data dir: {conf_value}")
            if len(conf_value) <= 0:
                ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_OCR_DATA_DIRECTORY, self.ocr_data_dir)
                if ec != 0:
                    return ec
        else:
            ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_MODEL_DIRECTORY, self.model_dir)
            if ec != 0:
                return ec
            ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_OCR_DATA_DIRECTORY, self.ocr_data_dir)
            if ec != 0:
                return ec

        ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_LOG_VERBOSITY, str(self.log_verbosity))
        if ec != 0:
            return ec
        ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_GLOBAL_LOG_DIRECTORY, self.log_dir)
        if ec != 0:
            return ec

        return 0 # 성공


    def errorResult(self, img_file, ec):
        return img_file, 0, "", ec, ""


    def recog(self, form_ocr_mode, form_file, img_file):

        start = time.time()

        ec = c_int()
        fp_ptr = self.IZ_form_createFormParam(byref(ec))
        if ec.value != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec.value)
        fp_ptr = c_void_p(fp_ptr)

        # conf 파일이 있으면 우선 적용함.
        # conf 파일에는 반드시 model_dir, ocr data dir이 설정되어 있어야 함.
        ec = self.set_required_conf(fp_ptr)
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_FORM_FILEPATH, form_file)
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        ec = self.set_conf (fp_ptr, self.IZ_FORM_CONF_PROCESS_MODE, str(form_ocr_mode))
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        resultObj = c_void_p()
        ec = self.IZ_form_initIzFormResult(byref(resultObj))
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        # 이미지 파일 열기
        # 한글파일명 처리를 위해서 fromfile와 imdecode 사용
        img_array = np.fromfile(img_file, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
        # img = cv2.imread(img_file)
        if img is None:
            print(f"error - Could not find image file. '{img_file}'")
            return self.errorResult(img_file, -1)

        # print(img.shape)
        if len(img.shape) == 2:
            height, width = img.shape
            bpp = 8
        else:
            height, width, depth = img.shape
            bpp = depth * 8

        imgBuffer=img.ctypes
        # print(f"width: {width}, height: {height}, bpp: {bpp}" )

        ec = self.IZ_form_setImage(fp_ptr, imgBuffer, width, height, bpp, 255, True)
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        ec = self.IZ_form_processRecognition (fp_ptr, resultObj)
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        ec = self.IZ_form_analyzeDocumentSet (fp_ptr, resultObj)
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        result_json = c_char_p()
        ec = self.IZ_form_getResultJson (resultObj, byref(result_json))
        if ec != 0:
            self.print_err(ec)
            return self.errorResult(img_file, ec)

        result_json = result_json.value.decode()
        if result_json:
            result_json = json.loads(result_json)

        self.IZ_form_freeIzFormResult(byref(resultObj))
        self.IZ_form_destroyFormParam(byref(fp_ptr))

        result_simple = self.simple_result(form_ocr_mode, form_file, img_file, result_json)

        elapsed = time.time() - start

        result = {
            "img_file": img_file,
            "elapsed": elapsed,
            "result_simple": result_simple,
            "ec": ec,
            "form_task_id": result_json['form_task_id'],
            "result_json": result_json
        }
        return result


    def simple_result(self, form_ocr_mode, form_file, img_file, result_json):

        strResult = ""
        strResult += f"form:  {form_file}\n"
        strResult += f"image: {img_file}\n"
        for doc in result_json["documents"]:
            formId = doc["formId"]
            formName = doc["formName"]
            fieldDefine = doc["fieldDefine"]
            strResult += f'\tformOcrMode: {form_ocr_mode}\n'
            strResult += f'\tformName: {formName} ({formId})\n'
            for block in doc["blocks"]:
                for field in block["fields"]:
                    fieldId = field["fieldId"]
                    fieldName = [s["fieldName"] for s in fieldDefine if fieldId == s["fieldId"]]
                    text = field["text"]
                    region = field["region"]
                    strFieldInfo = f'{fieldName[0]}({fieldId}):'
                    strResult += f'\t{strFieldInfo:20} {str(region):24} {text}\n'
        strResult += "\n"

        return strResult



if __name__ == '__main__':
    ocr_result = None
    result_json = None
    try:
        form_ocr = IzFormOcr(dll_dir="../../../bin/Release/x64")
        result_json, result_simple = form_ocr.recog(3, "./data/fullText_shkim.xml", "./data/classify_001.jpg")
    except Exception as e:
        print(f"error - {e}")

    if result_json is None:
        print("no result")
        exit()

    with open("./data/ocr_result.json", "w", encoding="utf-8") as fp:
        json.dump(result_json, fp, ensure_ascii=False, indent=2)
    with open("./data/ocr_result.txt", "w", encoding="utf-8") as fp:
        fp.write(result_simple)

    print("done.")


'''
    def get_result(self, resultObj):

        formDocuments = {}
        documents = []

        IntPointer = POINTER(c_int)
        docCount = self.IZ_form_getDocumentCount (resultObj)
        for iDoc in range(docCount):
            formDocument = {}

            # print("-----------------------------------------------------------")
            # print(f"[{iDoc}] document")
            pageCount = self.IZ_form_getDocumentPageCount (resultObj, iDoc)
            # print(f"\tpage count: {pageCount}")

            imgIdx = []
            imgFile = []
            tmpMsg = " (image index: "
            for iPage in range(pageCount):
                iImage = self.IZ_form_getImageIndex (resultObj, iDoc, iPage)
                if (iPage > 0):
                    tmpMsg += ", "
                tmpMsg += f"{iImage}"
                imgIdx.append(iImage)
                # imgFile.append(os.path.basename(file_list_img[iImage]))
            tmpMsg += ")"
            # print(tmpMsg)
            formDocument["imageIndex"] = imgIdx
            formDocument["imageFile"] = imgFile

            # 결과 확인
            id = c_wchar_p()
            self.IZ_form_getFormInfo (resultObj, iDoc, IZ_FORM_SUB_ITEM_FORM_ID, byref(id))
            # print(f"\tform id: {id.value}")
            formDocument["formId"] = id.value;

            strName = c_wchar_p()
            self.IZ_form_getFormInfo (resultObj, iDoc, IZ_FORM_SUB_ITEM_FORM_NAME, byref(strName))
            # print(f"\tform name: {strName.value}")
            formDocument["formName"] = strName.value

            noField = self.IZ_form_getDefinedFieldCount (resultObj, iDoc)
            # print(f"\tfield count: {noField}")

            fieldDefines = []
            for iField in range(noField):
                fieldId = IntPointer(c_int())

                fieldName = c_wchar_p()
                security = IntPointer(c_int())
                categoryId = IntPointer(c_int())
                self.IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_ID, byref(fieldId))
                self.IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_NAME, byref(fieldName))
                self.IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_SECURITY, byref(security))
                self.IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_CATEGORY, byref(categoryId))

                # print(f"\t\t[{iField}] id: {fieldId[0]}, {fieldName.value}, security: {security[0]}, category: {categoryId[0]}")
                fieldDefine = {}
                fieldDefine["fieldId"] = fieldId[0]
                fieldDefine["fieldName"] = fieldName.value
                fieldDefine["security"] = True if security[0] == 1 else False
                fieldDefine["categoryId"] = categoryId[0]
                fieldDefines.append(fieldDefine)
            formDocument["fieldDefine"] = fieldDefines

            noBlock = self.IZ_form_getBlockCount (resultObj, iDoc)
            # print(f"\tblock count: {noBlock}")

            blocks = []
            for iBlock in range(noBlock):
                blockId = IZ_form_getBlockId(resultObj, iDoc, iBlock)
                noField = IZ_form_getBlockFieldCount (resultObj, iDoc, iBlock)
                multiblock = IntPointer(c_int())
                IZ_form_getBlockAttribute (resultObj, iDoc, iBlock, IZ_FORM_SUB_ITEM_MULTI_BLOCK, byref(multiblock))
                # print(f"\t\t[{iBlock}] field count: {noField}, fieldblock: {multiblock[0]}")
                block = {}
                block["blockId"] = blockId
                block["multiblock"] = True if multiblock[0] == 1 else False

                fields = []
                for iField in range(noField):
                    fieldId = IntPointer(c_int())
                    strResult = c_wchar_p()
                    region = IntPointer(c_int())
                    score = IntPointer(c_int())
                    pageIndex = IntPointer(c_int())
                    security = IntPointer(c_int())
                    categoryId = IntPointer(c_int())

                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_ID, byref(fieldId))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_RECOG_STRING, byref(strResult))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_REGION, byref(region))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_SCORE, byref(score))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_PAGE_INDEX, byref(pageIndex))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_SECURITY, byref(security))
                    IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_CATEGORY, byref(categoryId))
                    imageIndex = IZ_form_getImageIndex (resultObj, iDoc, pageIndex[0])
                    tmpMsg = f"\t\t\t[{iField}] id: {fieldId[0]}, pageIndex: {pageIndex[0]}, imageIndex: {imageIndex}"
                    tmpMsg += f", security: {security[0]}, category: {categoryId[0]}, result: {strResult.value}"
                    tmpMsg += f", ({region[0]}, {region[1]}, {region[2]}, {region[3]}), score: {score[0]}"
                    # print(tmpMsg)
                    field = {}
                    field["imageIndex"] = imageIndex
                    # field["imageFile"] = os.path.basename(file_list_img[imageIndex])
                    field["pageIndex"] = pageIndex[0]
                    field["fieldId"] = fieldId[0]
                    field["security"] = True if security[0] == 1 else False
                    field["categoryId"] = categoryId[0]
                    field["text"] = strResult.value
                    field["region"] = [region[0], region[1], region[2], region[3]]
                    field["score"] = score[0]

                    wordObj = c_void_p()
                    IZ_form_getBlockFieldResult(resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_WORD_OBJ, byref(wordObj))
                    noWord = IZ_form_getFieldWordCount (wordObj);

                    words = []
                    for iWord in range(noWord):
                        strWord = c_wchar_p()
                        wordRegion = IntPointer(c_int())
                        wordScore = IntPointer(c_int())
                        ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_RECOG_STRING, byref(strWord))
                        ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_REGION, byref(wordRegion))
                        ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_SCORE, byref(wordScore))
                        word = {}
                        word["text"] = strWord.value
                        word["region"] = [wordRegion[0], wordRegion[1], wordRegion[2], wordRegion[3]]
                        word["confidence"] = wordScore[0]
                        words.append(word)
                    field["words"] = words
                    fields.append(field)

                block["fields"] = fields
                blocks.append(block)
            formDocument["blocks"] = blocks
            documents.append(formDocument)
        formDocuments["documents"] = documents


def processFormOcr_multi(params):
    form_ocr_dll = params[0]
    i = params[1]
    form_ocr_mode = params[2]
    form_file = params[3]
    img_file = params[4]
    result_dir = params[5]
    return process_form_ocr(form_ocr_dll, i, form_ocr_mode, form_file, img_file, result_dir)


def process_form_ocr(form_ocr_dll, i, form_ocr_mode, form_file, img_file, result_dir):

    IZ_FORM_CONF_CONFIG_FILEPATH          = 1  # 환경설정 정보 xml 파일명
    IZ_FORM_CONF_FORM_FILEPATH            = 2  # 서식정보파일명(비정형)
    IZ_FORM_CONF_MODEL_DIRECTORY          = 3  # 인식모델 디렉토리
    IZ_FORM_CONF_OCR_DATA_DIRECTORY       = 4  # ocrData 디렉토리
    IZ_FORM_CONF_PROCESS_MODE             = 5  # 처리모드
    IZ_FORM_CONF_IMAGE_ORIENTATION        = 6  #입력 이미지의 회전된 각도
    IZ_FORM_CONF_NUM_THREAD               = 7  # 병렬처리시 스레드 개수
    IZ_FORM_CONF_SKEW_CORRECTION          = 8  # skew 보정 수행유무
    IZ_FORM_CONF_REDUCE_IMAGE_SIZE        = 9  # 이미지 축소 해상도 (단위: pixel)
    IZ_FORM_CONF_RECOG_LANG_TYPE          = 10 # 인식언어타입
    IZ_FORM_CONF_TE_DOC_TYPE              = 11 # [텍스트라인 추출] 문서 타입
    IZ_FORM_CONF_TE_DOC_SUB_TYPE          = 12 # [텍스트라인 추출] 문서특성 옵션 (세부처리 옵션)
    IZ_FORM_CONF_TE_REDUCERATIO16         = 13 # [텍스트라인 추출] 축소 비율 (0 ~ 16)
    IZ_FORM_CONF_TE_INVERSE_TYPE          = 14 # [텍스트라인 추출] 역상처리 방식
    IZ_FORM_CONF_RESULT_STR_ENCODING      = 15 # 인식결과 문자열 인코딩
    IZ_FORM_CONF_SIZE_OF_WCHAR            = 16 # 인식결과 문자의 wchar_t size
    IZ_FORM_CONF_RESULT_ENDIAN_TYPE       = 17 # 인식결과 문자열 endian type
    IZ_FORM_CONF_LOG_VERBOSITY            = 18 # 로그 상세출력 설정
    IZ_FORM_CONF_GLOBAL_LOG_DIRECTORY     = 19 # 모듈의 모든 로그 저장 디렉토리
    IZ_FORM_CONF_INPUT_IMAGE_LOG_FILEPATH = 20 # 모듈 입력 이미지로그 파일경로
    IZ_FORM_CONF_PROGRESS_LOG_FILEPATH    = 21 # 프로그레스 로그 파일경로
    IZ_FORM_CONF_PROGRESS_LOG_OVERWRITE   = 22 # 신규 로그를 저장할 때 기존내용을 삭제할지 유무
    IZ_FORM_CONF_PROGRESS_LOG_MAX_SIZE    = 23 # 로그파일 최대 크기(byte)
    IZ_FORM_CONF_AUTOCROP_OBJECT_TYPE     = 24 # AutoCrop 옵션: 대상 물체 타입 지정
    IZ_FORM_CONF_AUTOCROP_INSIDE_BOUND    = 25 # AutoCrop 옵션: 반드시 포함되어야 할 영역 지정
    IZ_FORM_CONF_EXECUTE_FORM_ID          = 26 # 수행할 서식의 form id를 지정. 지정된 서식만 처리

    IZ_FORM_SUB_ITEM_FORM_ID              =	1  # 서식 ID
    IZ_FORM_SUB_ITEM_FORM_NAME            =	2  # 서식 이름
    IZ_FORM_SUB_ITEM_MULTI_BLOCK          = 3  # 결과에 여러블록 출력 유무
    IZ_FORM_SUB_ITEM_PAGE_INDEX           =	4  # 페이지 인덱스
    IZ_FORM_SUB_ITEM_FIELD_ID             =	5  # 필드 ID
    IZ_FORM_SUB_ITEM_FIELD_NAME           =	6  # 필드 이름
    IZ_FORM_SUB_ITEM_FIELD_SECURITY       = 7  # 필드 보안유무
    IZ_FORM_SUB_ITEM_FIELD_CATEGORY       = 8  # 필드 카테고리 id
    IZ_FORM_SUB_ITEM_RECOG_STRING         = 9  # 인식된 문자열
    IZ_FORM_SUB_ITEM_REGION               = 10 # 인식된 영역
    IZ_FORM_SUB_ITEM_SCORE                = 11 # 정확도 점수
    IZ_FORM_SUB_ITEM_WORD_OBJ             = 12 # word 정보 객체

    IZ_form_getVersion = form_ocr_dll['IZ_form_getVersion']
    IZ_form_getVersion.restype = c_char_p

    IZ_form_getFormXmlVersion = form_ocr_dll['IZ_form_getFormXmlVersion']
    IZ_form_getFormXmlVersion.restype = c_char_p

    IZ_form_getErrorMessage = form_ocr_dll['IZ_form_getErrorMessage']
    IZ_form_getErrorMessage.argtypes = [c_int]
    IZ_form_getErrorMessage.restype = c_char_p

    IZ_form_createFormParam = form_ocr_dll['IZ_form_createFormParam']
    IZ_form_createFormParam.argtypes = [POINTER(c_int)]
    IZ_form_createFormParam.restype = c_void_p

    IZ_form_destroyFormParam = form_ocr_dll['IZ_form_destroyFormParam']
    IZ_form_destroyFormParam.argtypes = [POINTER(c_void_p)]

    IZ_form_setConfigurations = form_ocr_dll['IZ_form_setConfigurations']
    IZ_form_setConfigurations.argtypes = [c_void_p, c_int, c_char_p]
    IZ_form_setConfigurations.restype = c_int

    IZ_form_getConfigurations = form_ocr_dll['IZ_form_getConfigurations']

    IZ_form_setRoi = form_ocr_dll['IZ_form_setRoi']
    IZ_form_setRoi.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
    IZ_form_setRoi.restype = c_int

    IZ_form_setImage = form_ocr_dll['IZ_form_setImage']
    IZ_form_initIzFormResult = form_ocr_dll['IZ_form_initIzFormResult']
    IZ_form_processRecognition = form_ocr_dll['IZ_form_processRecognition']
    IZ_form_analyzeDocumentSet = form_ocr_dll['IZ_form_analyzeDocumentSet']
    IZ_form_freeIzFormResult = form_ocr_dll['IZ_form_freeIzFormResult']

    IZ_form_getDocumentCount = form_ocr_dll['IZ_form_getDocumentCount']
    IZ_form_getDocumentPageCount = form_ocr_dll['IZ_form_getDocumentPageCount']
    IZ_form_getImageIndex = form_ocr_dll['IZ_form_getImageIndex']
    IZ_form_getFormInfo = form_ocr_dll['IZ_form_getFormInfo']
    IZ_form_getDefinedFieldCount = form_ocr_dll['IZ_form_getDefinedFieldCount']
    IZ_form_getDefinedFieldInfo = form_ocr_dll['IZ_form_getDefinedFieldInfo']
    IZ_form_getBlockCount = form_ocr_dll['IZ_form_getBlockCount']
    IZ_form_getBlockId = form_ocr_dll['IZ_form_getBlockId']
    IZ_form_getBlockAttribute = form_ocr_dll['IZ_form_getBlockAttribute']
    IZ_form_getBlockFieldCount = form_ocr_dll['IZ_form_getBlockFieldCount']
    IZ_form_getBlockFieldResult = form_ocr_dll['IZ_form_getBlockFieldResult']
    IZ_form_getFieldWordCount = form_ocr_dll['IZ_form_getFieldWordCount']
    IZ_form_getFieldWordResult = form_ocr_dll['IZ_form_getFieldWordResult']
    IZ_form_getResultJson = form_ocr_dll['IZ_form_getResultJson']


    def printErr (ec):
        errmsg = IZ_form_getErrorMessage(ec)
        errmsg =str(errmsg,'utf-8')
        print(str(ec) + " " + errmsg)


    # print(f"inziFormOcr v{str(IZ_form_getVersion(), 'utf-8')}")
    # print(f"inziFormOcr xml v{str(IZ_form_getFormXmlVersion(), 'utf-8')}")

    start = time.time()

    ec = c_int()
    fp_ptr = IZ_form_createFormParam(byref(ec))
    fp_ptr = c_void_p(fp_ptr)
    # if ec != 0:
    #     printErr(ec)

    ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_FORM_FILEPATH, bytes(form_file, encoding='utf-8'))
    ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_MODEL_DIRECTORY, bytes("../data/model", encoding='utf-8'))
    ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_OCR_DATA_DIRECTORY, bytes("../data/ocrData", encoding='utf-8'))
    ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_PROCESS_MODE, bytes(str(form_ocr_mode), encoding='utf-8'))

    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_LOG_VERBOSITY, bytes('3', encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_GLOBAL_LOG_DIRECTORY, bytes('log', encoding='utf-8'))

    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_FORM_FILEPATH, bytes(confInfo["formFile"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_MODEL_DIRECTORY, bytes(confInfo["modelDir"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_OCR_DATA_DIRECTORY, bytes(confInfo["ocrDataDir"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_PROCESS_MODE, bytes(str(confInfo["processMode"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_LOG_VERBOSITY, bytes(str(confInfo["logVerbosity"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_GLOBAL_LOG_DIRECTORY, bytes(confInfo["logDir"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_IMAGE_ORIENTATION, bytes(confInfo["imgOrientaion"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_NUM_THREAD, bytes(str(confInfo["numThread"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_SKEW_CORRECTION, b"true" if confInfo["skewCorrection"] else b"false")
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_REDUCE_IMAGE_SIZE, bytes(str(confInfo["reduceImageSize"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_TE_DOC_TYPE, bytes(confInfo["TeDocumentType"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_TE_DOC_SUB_TYPE, bytes(confInfo["TeDocumentSubOption"], encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_TE_REDUCERATIO16, bytes(str(confInfo["TeReduceRatio16"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_TE_INVERSE_TYPE, bytes(str(confInfo["TeInverseType"]), encoding='utf-8'))
    # ec = IZ_form_setConfigurations (fp_ptr, IZ_FORM_CONF_PROGRESS_LOG_OVERWRITE, b"true" if confInfo["ProgressLogOverwrite"] else b"false")

    # confBuff = create_string_buffer(512)
    # ec = IZ_form_getConfigurations (fp_ptr, IZ_FORM_CONF_FORM_FILEPATH, confBuff)
    # print('form file path: ' + str(confBuff, 'utf-8'))
    # ec = IZ_form_getConfigurations (fp_ptr, IZ_FORM_CONF_MODEL_DIRECTORY, confBuff)
    # print('form file path: ' + str(confBuff, 'utf-8'))
    # ec = IZ_form_getConfigurations (fp_ptr, IZ_FORM_CONF_OCR_DATA_DIRECTORY, confBuff)
    # print('form file path: ' + str(confBuff, 'utf-8'))

    resultObj = c_void_p()
    ec = IZ_form_initIzFormResult(byref(resultObj))
    if ec != 0:
        printErr(ec)

    img = cv2.imread(img_file)
    height, width, depth = img.shape
    bpp = depth * 8
    imgBuffer=img.ctypes
    # print(f"width: {width}, height: {height}, bpp: {bpp}" )

    ec = IZ_form_setImage(fp_ptr, imgBuffer, width, height, bpp, 255, True)
    if ec != 0:
        printErr(ec)

    ec = IZ_form_processRecognition (fp_ptr, resultObj)
    if ec != 0:
        printErr(ec)

    ec = IZ_form_analyzeDocumentSet (fp_ptr, resultObj)
    if ec != 0:
        printErr(ec)

    # strResultJson = create_string_buffer(512)
    # strResultJson = IZ_form_getResultJson (resultObj)
    # print("strResultJson: ", strResultJson, " end\n")











    formDocuments = {}
    documents = []

    IntPointer = POINTER(c_int)
    docCount = IZ_form_getDocumentCount (resultObj)
    for iDoc in range(docCount):
        formDocument = {}

        # print("-----------------------------------------------------------")
        # print(f"[{iDoc}] document")
        pageCount = IZ_form_getDocumentPageCount (resultObj, iDoc)
        # print(f"\tpage count: {pageCount}")

        imgIdx = []
        imgFile = []
        tmpMsg = " (image index: "
        for iPage in range(pageCount):
            iImage = IZ_form_getImageIndex (resultObj, iDoc, iPage)
            if (iPage > 0):
                tmpMsg += ", "
            tmpMsg += f"{iImage}"
            imgIdx.append(iImage)
            # imgFile.append(os.path.basename(file_list_img[iImage]))
        tmpMsg += ")"
        # print(tmpMsg)
        formDocument["imageIndex"] = imgIdx
        formDocument["imageFile"] = imgFile

        # 결과 확인
        id = c_wchar_p()
        IZ_form_getFormInfo (resultObj, iDoc, IZ_FORM_SUB_ITEM_FORM_ID, byref(id))
        # print(f"\tform id: {id.value}")
        formDocument["formId"] = id.value;

        strName = c_wchar_p()
        IZ_form_getFormInfo (resultObj, iDoc, IZ_FORM_SUB_ITEM_FORM_NAME, byref(strName))
        # print(f"\tform name: {strName.value}")
        formDocument["formName"] = strName.value

        noField = IZ_form_getDefinedFieldCount (resultObj, iDoc)
        # print(f"\tfield count: {noField}")

        fieldDefines = []
        for iField in range(noField):
            fieldId = IntPointer(c_int())

            fieldName = c_wchar_p()
            security = IntPointer(c_int())
            categoryId = IntPointer(c_int())
            IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_ID, byref(fieldId))
            IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_NAME, byref(fieldName))
            IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_SECURITY, byref(security))
            IZ_form_getDefinedFieldInfo (resultObj, iDoc, iField, IZ_FORM_SUB_ITEM_FIELD_CATEGORY, byref(categoryId))

            # print(f"\t\t[{iField}] id: {fieldId[0]}, {fieldName.value}, security: {security[0]}, category: {categoryId[0]}")
            fieldDefine = {}
            fieldDefine["fieldId"] = fieldId[0]
            fieldDefine["fieldName"] = fieldName.value
            fieldDefine["security"] = True if security[0] == 1 else False
            fieldDefine["categoryId"] = categoryId[0]
            fieldDefines.append(fieldDefine)
        formDocument["fieldDefine"] = fieldDefines

        noBlock = IZ_form_getBlockCount (resultObj, iDoc)
        # print(f"\tblock count: {noBlock}")

        blocks = []
        for iBlock in range(noBlock):
            blockId = IZ_form_getBlockId(resultObj, iDoc, iBlock)
            noField = IZ_form_getBlockFieldCount (resultObj, iDoc, iBlock)
            multiblock = IntPointer(c_int())
            IZ_form_getBlockAttribute (resultObj, iDoc, iBlock, IZ_FORM_SUB_ITEM_MULTI_BLOCK, byref(multiblock))
            # print(f"\t\t[{iBlock}] field count: {noField}, fieldblock: {multiblock[0]}")
            block = {}
            block["blockId"] = blockId
            block["multiblock"] = True if multiblock[0] == 1 else False

            fields = []
            for iField in range(noField):
                fieldId = IntPointer(c_int())
                strResult = c_wchar_p()
                region = IntPointer(c_int())
                score = IntPointer(c_int())
                pageIndex = IntPointer(c_int())
                security = IntPointer(c_int())
                categoryId = IntPointer(c_int())

                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_ID, byref(fieldId))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_RECOG_STRING, byref(strResult))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_REGION, byref(region))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_SCORE, byref(score))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_PAGE_INDEX, byref(pageIndex))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_SECURITY, byref(security))
                IZ_form_getBlockFieldResult (resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_FIELD_CATEGORY, byref(categoryId))
                imageIndex = IZ_form_getImageIndex (resultObj, iDoc, pageIndex[0])
                tmpMsg = f"\t\t\t[{iField}] id: {fieldId[0]}, pageIndex: {pageIndex[0]}, imageIndex: {imageIndex}"
                tmpMsg += f", security: {security[0]}, category: {categoryId[0]}, result: {strResult.value}"
                tmpMsg += f", ({region[0]}, {region[1]}, {region[2]}, {region[3]}), score: {score[0]}"
                # print(tmpMsg)
                field = {}
                field["imageIndex"] = imageIndex
                # field["imageFile"] = os.path.basename(file_list_img[imageIndex])
                field["pageIndex"] = pageIndex[0]
                field["fieldId"] = fieldId[0]
                field["security"] = True if security[0] == 1 else False
                field["categoryId"] = categoryId[0]
                field["text"] = strResult.value
                field["region"] = [region[0], region[1], region[2], region[3]]
                field["score"] = score[0]

                wordObj = c_void_p()
                IZ_form_getBlockFieldResult(resultObj, iDoc, iBlock, iField, IZ_FORM_SUB_ITEM_WORD_OBJ, byref(wordObj))
                noWord = IZ_form_getFieldWordCount (wordObj);

                words = []
                for iWord in range(noWord):
                    strWord = c_wchar_p()
                    wordRegion = IntPointer(c_int())
                    wordScore = IntPointer(c_int())
                    ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_RECOG_STRING, byref(strWord))
                    ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_REGION, byref(wordRegion))
                    ec = IZ_form_getFieldWordResult (wordObj, iWord, IZ_FORM_SUB_ITEM_SCORE, byref(wordScore))
                    word = {}
                    word["text"] = strWord.value
                    word["region"] = [wordRegion[0], wordRegion[1], wordRegion[2], wordRegion[3]]
                    word["confidence"] = wordScore[0]
                    words.append(word)
                field["words"] = words
                fields.append(field)

            block["fields"] = fields
            blocks.append(block)
        formDocument["blocks"] = blocks
        documents.append(formDocument)
    formDocuments["documents"] = documents

    IZ_form_freeIzFormResult(byref(resultObj))
    IZ_form_destroyFormParam(byref(fp_ptr))



    # basename = os.path.basename(img_file)
    # file_name = os.path.splitext(basename)[0]

    strResult = ""
    strResult += f"form:  {form_file}\n"
    strResult += f"image: {img_file}\n"
    for doc in formDocuments["documents"]:
        formId = doc["formId"]
        formName = doc["formName"]
        fieldDefine = doc["fieldDefine"]
        strResult += f'\tformOcrMode: {form_ocr_mode}\n'
        strResult += f'\tformName: {formName} ({formId})\n'
        for block in doc["blocks"]:
            for field in block["fields"]:
                fieldId = field["fieldId"]
                fieldName = [s["fieldName"] for s in fieldDefine if fieldId == s["fieldId"]]
                text = field["text"]
                region = field["region"]
                strFieldInfo = f'{fieldName[0]}({fieldId}):'
                strResult += f'\t{strFieldInfo:20} {str(region):24} {text}\n'
    strResult += "\n"

    # if result_dir:
    #     basename = os.path.basename(img_file)
    #     file_name = os.path.splitext(basename)[0]
    #     result_file_name = file_name + '_' + str(i + 1) + '.txt'
    #     result_file_path = os.path.join(result_dir, result_file_name)
    #     with open(result_file_path, "w", encoding='UTF8') as fp:
    #         fp.write(strResult)

    # if result_dir:
    #     basename = os.path.basename(img_file)
    #     file_name = os.path.splitext(basename)[0]
    #     result_file_name = file_name + '_' + str(i + 1) + '.json'
    #     result_file_path = os.path.join(result_dir, result_file_name)
    #     with open(result_file_path, "w", encoding='UTF8') as fp:
    #         json.dump(formDocuments, fp, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    # print(f'{i+1} time: {elapsed: .3f}')

    return img_file, elapsed, strResult
    # # 반환 결과 저장
    # if result_dir:
    #     result_file_name = img_file + '_' + type + '_' + str(i + 1) + '.json'
    #     result_file_path = os.path.join(result_dir, result_file_name)
    #     with open(result_file_path, 'w', encoding="UTF-8") as f:
    #         json.dump(response.json(), f, ensure_ascii=False, indent=2)
    # return formDocuments
'''
