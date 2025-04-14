cmake_minimum_required(VERSION 3.10)
project(StrikethroughDetector)

# C++11 사용
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# DLL 빌드 설정
add_library(strikethrough_detector SHARED strikethrough_detector.cpp)

# 윈도우에서 빌드 시 필요한 설정
if(WIN32)
    # 추가 컴파일러 옵션 설정 (Visual Studio 기준)
    set_target_properties(strikethrough_detector PROPERTIES
        DEFINE_SYMBOL "DLL_EXPORT"
        WINDOWS_EXPORT_ALL_SYMBOLS ON
    )
endif()

# 설치 경로 설정
install(TARGETS strikethrough_detector
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
)
