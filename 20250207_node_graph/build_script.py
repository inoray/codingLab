import os
import sys
from pathlib import Path

def create_build_command(main_script: str) -> str:
    """
    Nuitka 빌드 명령어를 생성하는 함수

    Args:
        main_script: 메인 Python 스크립트 파일명
    Returns:
        str: Nuitka 빌드 명령어
    """
    # 기본 명령어 구성
    cmd_parts = [
        f"python -m nuitka",
        f"--standalone",  # 독립 실행 파일 생성
        f"--windows-disable-console",  # 콘솔창 비활성화
        # f"--windows-icon-from-ico=icon/app.ico",  # 아이콘 설정

        # assets 디렉토리 포함
        f"--include-data-dir=assets=assets",

        # icon 디렉토리 포함
        f"--include-data-dir=icon=icon",

        # 최적화 옵션들
        f"--follow-imports",
        f"--assume-yes-for-downloads",
        f"--disable-console",
        f"--remove-output",

        # 필요한 모듈들 포함 (예시)
        f"--include-package=numpy",
        f"--include-package=pandas",

        # 메인 스크립트
        main_script
    ]

    return " ".join(cmd_parts)

def build_application():
    """애플리케이션 빌드 실행 함수"""
    # 현재 작업 디렉토리 저장
    current_dir = os.getcwd()

    # 메인 스크립트 파일명 (수정 필요)
    main_script = "form_relation_viewer.py"

    # 빌드 명령어 생성
    build_cmd = create_build_command(main_script)

    # 빌드 실행
    print("Building application...")
    print(f"Executing command: {build_cmd}")  # 실행되는 명령어 출력
    os.system(build_cmd)

    # 빌드 완료 후 정리
    output_dir = Path(current_dir) / "main.dist"
    if output_dir.exists():
        print(f"Build completed successfully!")
        print(f"Output directory: {output_dir}")
    else:
        print("Build failed!")

if __name__ == "__main__":
    build_application()
