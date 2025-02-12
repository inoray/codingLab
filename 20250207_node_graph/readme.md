# form relation viewer

## 설명

이 프로그램은 서식 XML 파일을 읽어서 관계도를 그려주는 프로그램입니다.
주요기능은 다음과 같습니다.

* 서식 XML 의 element, out field 간 관계도를 그래프로 표시
* 서식 XML 파일 간 관계도를 그래프로 표시

## 설치 및 실행

```bash
pip install -r requirements.txt
python form_relation_viewer.py
```

## 배포본 실행파일 만들기

### pyinstaller를 사용한 방법

```bash
# 설치가 안되어 있으면 설치
pip install pyinstaller

# add-data 옵션을 사용하여 실행파일에 필요한 파일을 포함시킬 수 있음
# 실행파일이 있는 디렉토리에 assets, icon 디렉토리를 만들고 파일을 넣어두면 실행파일에 포함됨
# 전체 디렉토리포함 사이즈 약 900Mb 정도 됨
pyinstaller -w --add-data "assets/*;assets" --add-data "icon/*;icon" form_relation_viewer.py

# onefile로 만들기 (약 340Mb 정도 됨)
pyinstaller --onefile -w --add-data "assets/*;assets" --add-data "icon/*;icon" form_relation_viewer.py
```

### pyside6-deploy를 사용한 방법

```bash
# 약 100Mb 정도 됨. 빌드시간이 오래 걸림
# 내부에서 nuitka를 사용함
# console 창이 뜸(제거 옵션이 없는 것 같음)
pyside6-deploy --name form_relation_viewer form_relation_viewer.py
```

### cx_Freeze를 사용한 방법

```bash
# cx_Freeze 설치(설치가 안되어 있으면 설치)
pip install cx_Freeze

# 빌드 (약 370Mb 정도 배포본이 생성됨)
python setup.py build
```

### PyOxidizer를 사용한 방법 (현재 잘 안됨)

```bash
# PyOxidizer 설치(설치가 안되어 있으면 설치)
pip install pyoxidizer

# 빌드 (약 370Mb 정도 배포본이 생성됨). pyoxidizer.bzl에 설정된 정보로 빌드됨
pyoxidizer build
```

* pyoxidizer.bzl 파일 작성 방법

초기 파일 생성
```bash
pyoxidizer init-config-file pyapp
```

pyoxidizer.bzl 파일 수정

```python
# pyoxidizer.bzl
def make_exe():
    # 기본 Python 배포판 설정 가져오기
    dist = default_python_distribution()

    # 리소스 파일을 "filesystem"에 위치시키도록 정책 설정
    policy = dist.make_python_packaging_policy()
    policy.resources_location = "filesystem"  # 또는 파일 크기가 작다면 "in-memory" 선택 가능

    # 인터프리터 설정 (여기서 'your_module'은 실제 실행할 모듈 이름으로 대체)
    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "your_module"

    return exe


def make_install(exe):
    # Create an object that represents our installed application file layout.
    files = FileManifest()

    files.add_path("assets/", strip_prefix="assets")
    files.add_path("icon/", strip_prefix="icon")

    # Add the generated executable to our install layout in the root directory.
    files.add_python_resource(".", exe)

    return files
```
