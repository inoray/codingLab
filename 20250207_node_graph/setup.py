from cx_Freeze import setup, Executable

# 포함할 파일 목록
include_files = [
    ('assets/', 'assets'),  # 'templates' 폴더를 포함
    ('icon/', 'icon'),        # 'icon' 폴더를 포함
]

# 빌드 옵션 설정
build_exe_options = {
    'include_files': include_files,
    # 필요에 따라 추가 옵션 설정 가능
}

# setup 함수 설정
setup(
    name='form relation viewer',  # 프로젝트 이름
    version='0.1',
    description='Your Application Description',
    options={'build_exe': build_exe_options},
    executables=[Executable('form_relation_viewer.py', base='Win32GUI')], # Win32GUI: 콘솔 없이 실행
)
