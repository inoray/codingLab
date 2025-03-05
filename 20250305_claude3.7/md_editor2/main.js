// main.js - Electron 메인 프로세스
const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const store = new Store();

let mainWindow;

function createWindow() {
  // 마지막으로 사용한 작업 폴더 복원 (없으면 앱 실행 위치 사용)
  const lastWorkingDir = store.get('workingDirectory') || app.getAppPath();

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');

  // 윈도우 상태 저장
  const saveWindowState = () => {
    if (!mainWindow.isMaximized() && !mainWindow.isMinimized()) {
      const bounds = mainWindow.getBounds();
      store.set('windowState', {
        width: bounds.width,
        height: bounds.height,
        x: bounds.x,
        y: bounds.y
      });
    }
    store.set('isMaximized', mainWindow.isMaximized());
  };

  mainWindow.on('resize', saveWindowState);
  mainWindow.on('move', saveWindowState);
  mainWindow.on('close', saveWindowState);

  // 앱 메뉴 설정
  const template = [
    {
      label: '파일',
      submenu: [
        {
          label: '새 파일',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.send('new-file')
        },
        {
          label: '폴더 열기',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const { canceled, filePaths } = await dialog.showOpenDialog({
              properties: ['openDirectory']
            });
            if (!canceled) {
              store.set('workingDirectory', filePaths[0]);
              mainWindow.webContents.send('folder-opened', filePaths[0]);
            }
          }
        },
        {
          label: '저장',
          accelerator: 'CmdOrCtrl+S',
          click: () => mainWindow.webContents.send('save-file')
        },
        {
          label: 'PDF로 내보내기',
          click: () => mainWindow.webContents.send('export-pdf')
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: '보기',
      submenu: [
        {
          label: '사이드바 토글',
          accelerator: 'CmdOrCtrl+B',
          click: () => mainWindow.webContents.send('toggle-sidebar')
        },
        {
          label: '미리보기 토글',
          accelerator: 'CmdOrCtrl+P',
          click: () => mainWindow.webContents.send('toggle-preview')
        },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        {
          label: '다크 모드 토글',
          click: () => mainWindow.webContents.send('toggle-dark-mode')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // 앱 종료 시 작업 디렉토리 저장
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // 작업 폴더 초기화
  mainWindow.webContents.once('did-finish-load', () => {
    mainWindow.webContents.send('init-working-directory', lastWorkingDir);

    // 저장된 다크모드 상태 복원
    const isDarkMode = store.get('darkMode', false);
    const isPreviewHidden = store.get('previewHidden', false);

    mainWindow.webContents.send('init-app-state', {
      isDarkModeState: isDarkMode,
      isPreviewHiddenState: isPreviewHidden
    });

    mainWindow.webContents.send('restore-dark-mode', isDarkMode);

    // 저장된 탭 정보 복원
    const savedTabs = store.get('openTabs', null);
    if (savedTabs && savedTabs.tabs && savedTabs.tabs.length > 0) {
      mainWindow.webContents.send('restore-tabs', savedTabs);
    }

    // 최대화 상태 복원
    if (store.get('isMaximized', false)) {
      mainWindow.maximize();
    }
  });

  // 종료 직전에 상태 저장
  mainWindow.on('close', () => {
    saveWindowState();
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// 저장 관련 IPC 핸들러 추가
ipcMain.on('save-app-state', (event, { isDarkMode, isPreviewHidden, openTabs }) => {
    store.set('darkMode', isDarkMode);
    store.set('previewHidden', isPreviewHidden); // 미리보기 상태 저장
    store.set('openTabs', openTabs);
  });

  // IPC 핸들러 추가 - 미리보기 상태 가져오기
ipcMain.handle('get-preview-state', () => {
    return store.get('previewHidden', false);
  });

// IPC 이벤트 핸들러
ipcMain.handle('read-directory', async (event, dirPath) => {
  try {
    const files = await fs.promises.readdir(dirPath, { withFileTypes: true });
    const fileStructure = await Promise.all(files.map(async file => {
      const filePath = path.join(dirPath, file.name);
      const stats = await fs.promises.stat(filePath);
      return {
        name: file.name,
        path: filePath,
        isDirectory: file.isDirectory(),
        size: stats.size,
        lastModified: stats.mtime
      };
    }));
    return fileStructure;
  } catch (error) {
    console.error('Error reading directory:', error);
    return [];
  }
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.promises.readFile(filePath, 'utf-8');
    return content;
  } catch (error) {
    console.error('Error reading file:', error);
    return '';
  }
});

ipcMain.handle('save-file', async (event, { filePath, content }) => {
  try {
    await fs.promises.writeFile(filePath, content, 'utf-8');
    return true;
  } catch (error) {
    console.error('Error saving file:', error);
    return false;
  }
});

ipcMain.handle('export-pdf', async (event, { filePath, htmlContent }) => {
  try {
    const pdfPath = filePath.replace(/\.md$/, '.pdf');
    const win = new BrowserWindow({
      show: false,
      webPreferences: { nodeIntegration: true }
    });

    await win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(htmlContent)}`);

    const pdfData = await win.webContents.printToPDF({
      marginsType: 0,
      printBackground: true,
      printSelectionOnly: false,
      landscape: false
    });

    await fs.promises.writeFile(pdfPath, pdfData);
    win.close();
    return pdfPath;
  } catch (error) {
    console.error('Error exporting PDF:', error);
    return null;
  }
});

// PDF 내보내기 - 파일명 선택 기능 추가
ipcMain.handle('export-pdf-with-dialog', async (event, { filePath, htmlContent, defaultName }) => {
    try {
      // 저장 다이얼로그 표시
      const { canceled, filePath: savePath } = await dialog.showSaveDialog({
        title: 'PDF로 내보내기',
        defaultPath: path.join(path.dirname(filePath), defaultName),
        filters: [
          { name: 'PDF 문서', extensions: ['pdf'] }
        ]
      });

      if (canceled) return null;

      // 임시 숨김 창 생성
      const win = new BrowserWindow({
        show: false,
        webPreferences: { nodeIntegration: true }
      });

      await win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(htmlContent)}`);

      const pdfData = await win.webContents.printToPDF({
        marginsType: 0,
        printBackground: true,
        printSelectionOnly: false,
        landscape: false
      });

      await fs.promises.writeFile(savePath, pdfData);
      win.close();
      return savePath;
    } catch (error) {
      console.error('Error exporting PDF:', error);
      return null;
    }
  });
