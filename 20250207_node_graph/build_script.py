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
        f"--onefile",  # 하나의 실행 파일로 묶기
        f"--windows-console-mode=disable", # 콘솔창 비활성화
        f"--windows-icon-from-ico=./assets/icon/app_icon.png",  # 아이콘 설정

        # Qt 플러그인 관련 설정
        f"--enable-plugin=pyside6",  # PySide6를 사용하는 경우

        # Qt 플러그인 포함
        f"--include-qt-plugins=platforms",
        f"--include-qt-plugins=styles",

        # assets 디렉토리 포함
        f"--include-data-dir=assets=assets",

        # 최적화 옵션들
        f"--follow-imports",
        f"--assume-yes-for-downloads",
        f"--remove-output",

        # 필요한 모듈들 포함 (예시)
        # f"--include-package=numpy",
        # f"--include-package=pandas",

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
    # output_dir = Path(current_dir) / "form_relation_viewer.dist"
    # if output_dir.exists():
    #     print(f"Build completed successfully!")
    #     print(f"Output directory: {output_dir}")
    # else:
    #     print("Build failed!")

if __name__ == "__main__":
    build_application()
