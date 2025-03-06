// renderer.js
const { ipcRenderer } = window.electron;
const path = window.path;

// DOM 요소
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebarResizeHandle = document.querySelector('.sidebar-resize-handle');
const fileTree = document.getElementById('file-tree');
const currentFolderPath = document.getElementById('current-folder-path');
const tabs = document.getElementById('tabs');
const newTabBtn = document.getElementById('new-tab');
const mdEditor = document.getElementById('md-editor');
const preview = document.getElementById('preview');
const wordCount = document.getElementById('word-count');
const toggleModeBtn = document.getElementById('toggle-mode');
const togglePreviewBtn = document.getElementById('toggle-preview'); // 추가: 미리보기 토글 버튼
const editorContainer = document.getElementById('editor-container'); // 추가: 에디터 컨테이너
const appContainer = document.querySelector('.app-container'); // 추가: app-container 요소 직접 참조

// 애플리케이션 상태
let currentWorkingDirectory = '';
let activeTabId = null;
let tabsData = [];
let isDarkMode = false;
let isPreviewHidden = true; // 추가: 미리보기 숨김 상태

// 임시 탭 상태 관리
let hasTemporaryTab = false;
let isEditing = false;

// 탭 ID 카운터
let tabCounter = 0;
// 미리보기 토글 기능 추가
togglePreviewBtn.addEventListener('click', () => {
    togglePreview();
  });

  // 미리보기 토글 함수
  function togglePreview() {
    editorContainer.classList.toggle('preview-hidden');
    isPreviewHidden = editorContainer.classList.contains('preview-hidden');

    // 아이콘 변경
    const icon = togglePreviewBtn.querySelector('i');
    if (isPreviewHidden) {
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    } else {
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    }

    saveAppState();
  }

  // IPC 이벤트 리스너 추가
  ipcRenderer.on('toggle-preview', () => {
    togglePreview();
  });

  // 앱 상태 저장 함수 확장
  function saveAppState() {
    // 저장할 탭 정보 생성
    const tabsToSave = tabsData.map(tab => ({
      title: tab.title,
      filePath: tab.filePath,
      content: tab.content,
      isTemporary: tab.isTemporary,
      isModified: tab.isModified
    }));

    // 현재 활성 탭 ID 인덱스로 변환하여 저장
    const activeTabIndex = tabsData.findIndex(tab => tab.id === activeTabId);

    // 상태 저장 요청
    ipcRenderer.send('save-app-state', {
      isDarkMode: isDarkMode,
      isPreviewHidden: isPreviewHidden, // 미리보기 상태 저장
      openTabs: {
        tabs: tabsToSave,
        activeTabIndex: activeTabIndex >= 0 ? activeTabIndex : null
      }
    });
  }

  // 미리보기 상태 복원 추가
  ipcRenderer.on('init-app-state', (event, { isDarkModeState, isPreviewHiddenState }) => {
    // 다크모드 상태 복원
    if (isDarkModeState) {
      document.body.classList.add('dark-mode');
      const darkModeIcon = toggleModeBtn.querySelector('i');
      darkModeIcon.classList.remove('fa-moon');
      darkModeIcon.classList.add('fa-sun');
      isDarkMode = true;
    }

    // 미리보기 상태 복원
    if (isPreviewHiddenState) {
        editorContainer.classList.add('preview-hidden');
        const previewIcon = togglePreviewBtn.querySelector('i');
        previewIcon.classList.remove('fa-eye');
        previewIcon.classList.add('fa-eye-slash');
        isPreviewHidden = true;
      } else {
        editorContainer.classList.remove('preview-hidden');
        const previewIcon = togglePreviewBtn.querySelector('i');
        previewIcon.classList.remove('fa-eye-slash');
        previewIcon.classList.add('fa-eye');
        isPreviewHidden = false;
      }
  });

// 사이드바 토글 - 버그 수정
sidebarToggle.addEventListener('click', () => {
  // 직접 app-container에 클래스를 추가/제거
  appContainer.classList.toggle('sidebar-hidden');
  const icon = sidebarToggle.querySelector('i');
  icon.classList.toggle('fa-chevron-left');
  icon.classList.toggle('fa-chevron-right');
});

// 사이드바 크기 조절
let isResizing = false;
let lastDownX = 0;

sidebarResizeHandle.addEventListener('mousedown', (e) => {
  isResizing = true;
  lastDownX = e.clientX;
  document.addEventListener('mousemove', resizeSidebar);
  document.addEventListener('mouseup', stopResizing);
  e.preventDefault();
});

function resizeSidebar(e) {
  if (!isResizing) return;
  const deltaX = e.clientX - lastDownX;
  const newWidth = sidebar.offsetWidth + deltaX;

  if (newWidth >= 150 && newWidth <= 400) {
    sidebar.style.width = `${newWidth}px`;
    lastDownX = e.clientX;
  }
}

function stopResizing() {
  isResizing = false;
  document.removeEventListener('mousemove', resizeSidebar);
  document.removeEventListener('mouseup', stopResizing);
}

// 다크 모드 토글
toggleModeBtn.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  const icon = toggleModeBtn.querySelector('i');
  icon.classList.toggle('fa-moon');
  icon.classList.toggle('fa-sun');
  isDarkMode = document.body.classList.contains('dark-mode');
  saveAppState();
});

// 다크모드 상태 복원
ipcRenderer.on('restore-dark-mode', (event, darkModeState) => {
    if (darkModeState) {
      document.body.classList.add('dark-mode');
      const icon = toggleModeBtn.querySelector('i');
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
      isDarkMode = true;
    }
  });

  // 탭 상태 복원
  ipcRenderer.on('restore-tabs', async (event, savedTabsData) => {
    if (!savedTabsData || !savedTabsData.tabs || savedTabsData.tabs.length === 0) return;

    // 기존 탭 데이터 초기화
    tabsData = [];
    hasTemporaryTab = false;

    // 저장된 탭 복원
    for (const tab of savedTabsData.tabs) {
      try {
        // 파일이 실제로 존재하는지 확인
        let content = tab.content;

        if (!tab.isTemporary && !tab.isModified) {
          // 변경되지 않은 파일은 디스크에서 최신 내용을 로드
          content = await ipcRenderer.invoke('read-file', tab.filePath);
        }

        const newTabId = `tab-${tabCounter++}`;
        tabsData.push({
          id: newTabId,
          title: tab.title,
          filePath: tab.filePath,
          content: content,
          isTemporary: tab.isTemporary,
          isModified: tab.isModified
        });

        if (tab.isTemporary) {
          hasTemporaryTab = true;
        }
      } catch (error) {
        console.error('탭 복원 중 오류:', error);
      }
    }

    // 탭 렌더링
    renderTabs();

    // 활성 탭 설정
    if (tabsData.length > 0) {
      const activeIndex = savedTabsData.activeTabIndex !== null ?
                          savedTabsData.activeTabIndex : 0;

      if (activeIndex >= 0 && activeIndex < tabsData.length) {
        setActiveTab(tabsData[activeIndex].id);
      } else {
        setActiveTab(tabsData[0].id);
      }
    }
  });

  // 탭 닫기
  function closeTab(tabId) {
    const tabIndex = tabsData.findIndex(tab => tab.id === tabId);

    if (tabIndex === -1) return;

    const isTemporary = tabsData[tabIndex].isTemporary;
    tabsData.splice(tabIndex, 1);

    if (isTemporary) {
      hasTemporaryTab = false;
    }

    if (activeTabId === tabId) {
      // 닫은 탭이 활성 탭이었을 경우 다른 탭 활성화
      if (tabsData.length > 0) {
        setActiveTab(tabsData[tabsData.length - 1].id);
      } else {
        clearEditor();
      }
    }

    renderTabs();
    saveAppState(); // 탭을 닫을 때 앱 상태 저장
  }

// 탭 활성화
function setActiveTab(tabId) {
    activeTabId = tabId;
    const activeTab = tabsData.find(tab => tab.id === tabId);

    if (activeTab) {
      // XML 태그가 있는 경우 이스케이프하여 표시
      let displayContent = activeTab.content
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      mdEditor.innerHTML = displayContent;

      console.log(activeTab.content)
      renderPreview(activeTab.content);
      updateWordCount(activeTab.content);

      // 로드 후 구문 하이라이트 적용
      setTimeout(() => highlightMarkdown(mdEditor), 10);
    }

    renderTabs();
    saveAppState();
}

// 작업 디렉토리 초기화
ipcRenderer.on('init-working-directory', async (event, dirPath) => {
  currentWorkingDirectory = dirPath;
  currentFolderPath.textContent = dirPath;
  await refreshFileTree();
});

// 폴더 열기 이벤트 처리
ipcRenderer.on('folder-opened', async (event, dirPath) => {
  currentWorkingDirectory = dirPath;
  currentFolderPath.textContent = dirPath;
  await refreshFileTree();
});

// 파일 트리 새로고침
async function refreshFileTree() {
  const files = await ipcRenderer.invoke('read-directory', currentWorkingDirectory);
  renderFileTree(files);
}

// 파일 트리 렌더링
function renderFileTree(files) {
    fileTree.innerHTML = '';

    // 폴더와 파일 분리 및 정렬
    const folders = files.filter(file => file.isDirectory).sort((a, b) => a.name.localeCompare(b.name));
    const markdownFiles = files.filter(file => !file.isDirectory && file.name.endsWith('.md')).sort((a, b) => a.name.localeCompare(b.name));
    const otherFiles = files.filter(file => !file.isDirectory && !file.name.endsWith('.md')).sort((a, b) => a.name.localeCompare(b.name));

    // 폴더 먼저 렌더링
    folders.forEach(folder => {
      const folderItem = document.createElement('div');
      folderItem.className = 'tree-item folder';
      folderItem.innerHTML = `<i class="fas fa-folder"></i> ${folder.name}`;
      folderItem.dataset.path = folder.path;

      // 폴더 클릭 이벤트
      folderItem.addEventListener('click', async (e) => {
        e.stopPropagation();
        await toggleFolder(folder.path, folderItem);
      });

      fileTree.appendChild(folderItem);
    });

    // 마크다운 파일 렌더링
    markdownFiles.forEach(file => {
      const fileItem = document.createElement('div');
      fileItem.className = 'tree-item file';
      fileItem.innerHTML = `<i class="fas fa-file-alt"></i> ${file.name}`;
      fileItem.dataset.path = file.path;

      // 단일 클릭 이벤트
      fileItem.addEventListener('click', (e) => {
        e.stopPropagation();
        handleFileClick(file.path);

        // 파일 선택 상태 표시
        document.querySelectorAll('.tree-item').forEach(item => {
          item.classList.remove('selected');
        });
        fileItem.classList.add('selected');
      });

      // 더블클릭 이벤트 추가
      fileItem.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        handleFileDoubleClick(file.path);
      });

      fileTree.appendChild(fileItem);
    });

    // 기타 파일 렌더링
    otherFiles.forEach(file => {
      const fileItem = document.createElement('div');
      fileItem.className = 'tree-item file';
      fileItem.innerHTML = `<i class="fas fa-file"></i> ${file.name}`;
      fileItem.dataset.path = file.path;
      fileItem.addEventListener('click', (e) => {
        e.stopPropagation();

        // 파일 선택 상태 표시
        document.querySelectorAll('.tree-item').forEach(item => {
          item.classList.remove('selected');
        });
        fileItem.classList.add('selected');
      });
      fileTree.appendChild(fileItem);
    });
  }
// 새로운 함수: 폴더 토글 (열기/닫기)
async function toggleFolder(folderPath, folderElement) {
    // 폴더 아이콘 요소
    const folderIcon = folderElement.querySelector('i');

    // 다음 형제 요소 확인
    const nextElement = folderElement.nextElementSibling;
    const isOpen = nextElement && nextElement.classList.contains('tree-children');

    // 이미 열려있는 경우 닫기
    if (isOpen) {
      nextElement.remove();
      folderIcon.classList.remove('fa-folder-open');
      folderIcon.classList.add('fa-folder');
      return;
    }

    // 닫혀있는 경우 열기
    folderIcon.classList.remove('fa-folder');
    folderIcon.classList.add('fa-folder-open');

    // 로딩 인디케이터 추가
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.textContent = '로딩 중...';
    loadingIndicator.style.marginLeft = '20px';
    loadingIndicator.style.fontSize = '0.8em';
    loadingIndicator.style.color = '#888';
    folderElement.after(loadingIndicator);

    try {
      // 폴더 내용 가져오기
      const files = await ipcRenderer.invoke('read-directory', folderPath);

      // 로딩 인디케이터 제거
      loadingIndicator.remove();

      // 하위 요소 컨테이너 생성
      const treeChildren = document.createElement('div');
      treeChildren.className = 'tree-children';

      // 폴더와 파일 분리 및 정렬
      const folders = files.filter(file => file.isDirectory).sort((a, b) => a.name.localeCompare(b.name));
      const markdownFiles = files.filter(file => !file.isDirectory && file.name.endsWith('.md')).sort((a, b) => a.name.localeCompare(b.name));
      const otherFiles = files.filter(file => !file.isDirectory && !file.name.endsWith('.md')).sort((a, b) => a.name.localeCompare(b.name));

      // 하위 폴더 렌더링
      folders.forEach(subfolder => {
        const subFolderItem = document.createElement('div');
        subFolderItem.className = 'tree-item folder';
        subFolderItem.innerHTML = `<i class="fas fa-folder"></i> ${subfolder.name}`;
        subFolderItem.dataset.path = subfolder.path;

        subFolderItem.addEventListener('click', async (e) => {
          e.stopPropagation();
          await toggleFolder(subfolder.path, subFolderItem);
        });

        treeChildren.appendChild(subFolderItem);
      });

      // 하위 마크다운 파일 렌더링
      markdownFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'tree-item file';
        fileItem.innerHTML = `<i class="fas fa-file-alt"></i> ${file.name}`;
        fileItem.dataset.path = file.path;

        fileItem.addEventListener('click', (e) => {
          e.stopPropagation();
          handleFileClick(file.path);

          // 파일 선택 상태 표시
          document.querySelectorAll('.tree-item').forEach(item => {
            item.classList.remove('selected');
          });
          fileItem.classList.add('selected');
        });

        // 더블클릭 이벤트 추가
        fileItem.addEventListener('dblclick', (e) => {
          e.stopPropagation();
          handleFileDoubleClick(file.path);
        });

        treeChildren.appendChild(fileItem);
      });

      // 하위 기타 파일 렌더링
      otherFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'tree-item file';
        fileItem.innerHTML = `<i class="fas fa-file"></i> ${file.name}`;
        fileItem.dataset.path = file.path;

        fileItem.addEventListener('click', (e) => {
          e.stopPropagation();

          // 파일 선택 상태 표시
          document.querySelectorAll('.tree-item').forEach(item => {
            item.classList.remove('selected');
          });
          fileItem.classList.add('selected');
        });

        treeChildren.appendChild(fileItem);
      });

      // 하위 요소가 있는 경우에만 추가
      if (folders.length > 0 || markdownFiles.length > 0 || otherFiles.length > 0) {
        folderElement.after(treeChildren);
      } else {
        // 비어있는 폴더인 경우 메시지 표시
        const emptyFolder = document.createElement('div');
        emptyFolder.className = 'tree-children';
        emptyFolder.innerHTML = '<div class="tree-item empty" style="font-style: italic; color: #888;">비어있는 폴더</div>';
        folderElement.after(emptyFolder);
      }
    } catch (error) {
      console.error('폴더 내용을 불러오는 중 오류 발생:', error);
      loadingIndicator.textContent = '오류 발생';
      loadingIndicator.style.color = 'red';

      // 3초 후 로딩 인디케이터 제거
      setTimeout(() => {
        loadingIndicator.remove();
        folderIcon.classList.remove('fa-folder-open');
        folderIcon.classList.add('fa-folder');
      }, 3000);
    }
  }

// 파일 클릭 처리
async function handleFileClick(filePath) {
  const fileName = path.basename(filePath);

  // 이미 열려있는 탭인지 확인
  const existingTabIndex = tabsData.findIndex(tab => tab.filePath === filePath);

  if (existingTabIndex !== -1) {
    // 이미 열려있는 탭 활성화
    setActiveTab(tabsData[existingTabIndex].id);
  } else {
    // 임시 탭 관리
    if (hasTemporaryTab) {
      // 기존 임시 탭 제거
      const tempTabIndex = tabsData.findIndex(tab => tab.isTemporary);
      if (tempTabIndex !== -1) {
        closeTab(tabsData[tempTabIndex].id);
      }
    }

    // 새 임시 탭 생성
    const content = await ipcRenderer.invoke('read-file', filePath);
    const newTabId = `tab-${tabCounter++}`;

    const newTab = {
      id: newTabId,
      title: fileName,
      filePath: filePath,
      content: content,
      isTemporary: true,
      isModified: false
    };

    tabsData.push(newTab);
    hasTemporaryTab = true;
    renderTabs();
    setActiveTab(newTabId);
  }
}

// 탭 렌더링
function renderTabs() {
  tabs.innerHTML = '';

  tabsData.forEach(tab => {
    const tabElement = document.createElement('div');
    tabElement.className = `tab ${tab.id === activeTabId ? 'active' : ''}`;
    tabElement.dataset.id = tab.id;

    const tabTitle = document.createElement('div');
    tabTitle.className = `tab-title ${tab.isTemporary ? 'temporary' : ''}`;
    tabTitle.textContent = tab.isModified ? `${tab.title} *` : tab.title;

    const closeButton = document.createElement('div');
    closeButton.className = 'tab-close';
    closeButton.innerHTML = '<i class="fas fa-times"></i>';
    closeButton.addEventListener('click', (e) => {
      e.stopPropagation();
      closeTab(tab.id);
    });

    tabElement.appendChild(tabTitle);
    tabElement.appendChild(closeButton);
    tabElement.addEventListener('click', () => setActiveTab(tab.id));

    tabs.appendChild(tabElement);
  });
}

// 탭 닫기
function closeTab(tabId) {
  const tabIndex = tabsData.findIndex(tab => tab.id === tabId);

  if (tabIndex === -1) return;

  const isTemporary = tabsData[tabIndex].isTemporary;
  tabsData.splice(tabIndex, 1);

  if (isTemporary) {
    hasTemporaryTab = false;
  }

  if (activeTabId === tabId) {
    // 닫은 탭이 활성 탭이었을 경우 다른 탭 활성화
    if (tabsData.length > 0) {
      setActiveTab(tabsData[tabsData.length - 1].id);
    } else {
      clearEditor();
    }
  }

  renderTabs();
}

// 미리보기 렌더링
function renderPreview(markdown) {
  preview.innerHTML = marked.parse(markdown);
  // 코드 블록 하이라이팅
  document.querySelectorAll('pre code').forEach(block => {
    hljs.highlightBlock(block);
  });
}

// 단어 수 업데이트
function updateWordCount(text) {
  if (!text) {
    wordCount.textContent = '0 단어';
    return;
  }

  // 마크다운 문법 제거 후 단어 수 계산
  const plainText = text.replace(/[#*~`_>-]/g, '').trim();
  const words = plainText.split(/\s+/).filter(word => word.length > 0);
  wordCount.textContent = `${words.length} 단어`;
}

// 에디터 초기화
function clearEditor() {
  mdEditor.innerHTML = '';
  preview.innerHTML = '';
  wordCount.textContent = '0 단어';
  activeTabId = null;
}

// 파일 더블클릭 처리 함수 추가
async function handleFileDoubleClick(filePath) {
    const fileName = path.basename(filePath);

    // 이미 열려있는 탭인지 확인
    const existingTabIndex = tabsData.findIndex(tab => tab.filePath === filePath);

    if (existingTabIndex !== -1) {
      // 이미 열려있는 탭이 임시 탭이면 작업 탭으로 변경
      if (tabsData[existingTabIndex].isTemporary) {
        tabsData[existingTabIndex].isTemporary = false;
        hasTemporaryTab = false;
        renderTabs();
      }
      setActiveTab(tabsData[existingTabIndex].id);
    } else {
      // 새 작업 탭 생성 (임시 탭이 아님)
      const content = await ipcRenderer.invoke('read-file', filePath);
      const newTabId = `tab-${tabCounter++}`;

      const newTab = {
        id: newTabId,
        title: fileName,
        filePath: filePath,
        content: content,
        isTemporary: false, // 임시 탭이 아닌 작업 탭으로 생성
        isModified: false
      };

      // 임시 탭 제거
      if (hasTemporaryTab) {
        const tempTabIndex = tabsData.findIndex(tab => tab.isTemporary);
        if (tempTabIndex !== -1) {
          tabsData.splice(tempTabIndex, 1);
        }
        hasTemporaryTab = false;
      }

      tabsData.push(newTab);
      renderTabs();
      setActiveTab(newTabId);
    }

    saveAppState();
  }

// 마크다운 구문 하이라이트 함수
function highlightMarkdown(editor) {
  const content = editor.innerHTML;
  if (!content) return;

  // 현재 커서 위치 저장
  const selection = window.getSelection();
  const range = selection.getRangeAt(0);
  const startOffset = range.startOffset;
  const startContainer = range.startContainer;

  // 구문 하이라이트 적용
  let highlightedContent = content
    // 헤더 (#, ##, ###)
    .replace(/^(#{1,6}\s+)(.+)$/gm, '<span class="header">$1$2</span>')
    // 굵은 텍스트 (**text**)
    .replace(/\*\*(.+?)\*\*/g, '<span class="bold">**$1**</span>')
    // 기울임 텍스트 (*text*)
    .replace(/\*([^*]+)\*/g, '<span class="italic">*$1*</span>')
    // 인라인 코드 (`code`)
    .replace(/`([^`]+)`/g, '<span class="code">`$1`</span>')
    // 링크 [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<span class="link">[$1]($2)</span>')
    // 목록 항목 (- item)
    .replace(/^(\s*[-*+]\s+)(.+)$/gm, '<span class="list-item">$1$2</span>')
    // 인용구 (> text)
    .replace(/^(\s*>\s+)(.+)$/gm, '<span class="blockquote">$1$2</span>')
    // 코드 블록 (```)
    .replace(/```[\s\S]*?```/g, (match) => `<span class="codeblock">${match}</span>`)
    // XML 태그
    .replace(/&lt;([^&]+)&gt;/g, '<span class="xml-tag">&lt;$1&gt;</span>');

  // 하이라이트된 내용 적용
  editor.innerHTML = highlightedContent;

  // 커서 위치 복원 시도
  try {
    const newRange = document.createRange();
    newRange.setStart(editor.childNodes[0] || editor, startOffset);
    newRange.collapse(true);
    selection.removeAllRanges();
    selection.addRange(newRange);
  } catch (e) {
    console.warn('커서 위치 복원 실패:', e);
  }
}

// 에디터 입력 처리 수정 - 하이라이트 추가
mdEditor.addEventListener('input', () => {
  // 현재 에디터 내용 가져오기
  let content = mdEditor.innerHTML;

  // XML 태그를 보존하기 위해 특수 처리
  if (content.includes('&lt;') && !content.includes('&amp;lt;')) {
    content = content.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  }

  if (activeTabId) {
    const activeTabIndex = tabsData.findIndex(tab => tab.id === activeTabId);
    if (activeTabIndex !== -1) {
      const tab = tabsData[activeTabIndex];

      // 내용이 변경되었는지 확인
      if (tab.content !== content) {
        if (tab.isTemporary) {
          tab.isTemporary = false;
          hasTemporaryTab = false;
        }

        tab.isModified = true;
        tab.content = content;
        renderTabs();

        renderPreview(content);
        updateWordCount(content);
        saveAppState();

        // 구문 하이라이트 적용
        setTimeout(() => highlightMarkdown(mdEditor), 10);
      }
    }
  }
});

// 새 파일 생성
newTabBtn.addEventListener('click', () => {
  const newTabId = `tab-${tabCounter++}`;
  const newFileName = `Untitled-${Date.now()}.md`;

  const newTab = {
    id: newTabId,
    title: newFileName,
    filePath: path.join(currentWorkingDirectory, newFileName),
    content: '',
    isTemporary: false,
    isModified: true
  };

  tabsData.push(newTab);
  renderTabs();
  setActiveTab(newTabId);
});

// IPC 이벤트 리스너
ipcRenderer.on('new-file', () => {
  newTabBtn.click();
});

// IPC 이벤트 리스너
ipcRenderer.on('save-file', async () => {
    if (!activeTabId) return;

    const activeTabIndex = tabsData.findIndex(tab => tab.id === activeTabId);
    if (activeTabIndex !== -1) {
      const tab = tabsData[activeTabIndex];

      // 파일 저장
      const success = await ipcRenderer.invoke('save-file', {
        filePath: tab.filePath,
        content: tab.content
      });

      if (success) {
        tab.isModified = false;
        renderTabs();
        refreshFileTree();
        saveAppState(); // 파일 저장 후 앱 상태 저장
      }
    }
    saveAppState(); // 파일 저장 후 앱 상태 저장
  });

ipcRenderer.on('export-pdf', async () => {
  if (!activeTabId) return;

  const activeTabIndex = tabsData.findIndex(tab => tab.id === activeTabId);
  if (activeTabIndex !== -1) {
    const tab = tabsData[activeTabIndex];

    // HTML 콘텐츠 생성
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
              Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 2cm;
            font-size: 14px;
            line-height: 1.5;
          }
          h1, h2, h3, h4, h5, h6 {
            margin-top: 1em;
            margin-bottom: 0.5em;
          }
          p { margin-bottom: 1em; }
          ul, ol { margin-left: 2em; margin-bottom: 1em; }
          pre {
            background-color: #f6f8fa;
            padding: 1em;
            border-radius: 3px;
            overflow: auto;
            margin-bottom: 1em;
          }
          blockquote {
            border-left: 4px solid #e0e0e0;
            padding-left: 1em;
            color: #6a737d;
            margin-bottom: 1em;
          }
        </style>
      </head>
      <body>
        ${preview.innerHTML}
      </body>
      </html>
    `;

    // PDF 내보내기 요청
    const pdfPath = await ipcRenderer.invoke('export-pdf-with-dialog', {
      filePath: tab.filePath,
      htmlContent: htmlContent,
      defaultName: tab.title.replace('.md', '.pdf')
    });

    if (pdfPath) {
      alert(`PDF가 성공적으로 저장되었습니다: ${pdfPath}`);
    }
  }
});

ipcRenderer.on('toggle-sidebar', () => {
  sidebarToggle.click();
});

ipcRenderer.on('toggle-dark-mode', () => {
  toggleModeBtn.click();
});

// 초기화
document.addEventListener('DOMContentLoaded', () => {
  // 메인 UI 설정
  mdEditor.focus();

  // 저장된 미리보기 상태 복원
  const savedPreviewState = ipcRenderer.invoke('get-preview-state', false);
  if (savedPreviewState) {
    editorContainer.classList.add('preview-hidden');
    const icon = togglePreviewBtn.querySelector('i');
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
    isPreviewHidden = true;
  }

  // 페이지 언로드 시 상태 저장
  window.addEventListener('beforeunload', () => {
    saveAppState();
  });

  // highlight.js 테마를 One Dark로 변경
  const linkElement = document.querySelector('link[href*="highlight"]');
  if (linkElement) {
    // highlight.js One Dark 테마로 변경
    linkElement.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/atom-one-dark.min.css';
  }
});
