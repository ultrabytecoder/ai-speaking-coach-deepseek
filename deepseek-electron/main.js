const { app, BrowserWindow, ipcMain } = require("electron");
const { WebSocketServer } = require('ws');

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadURL("https://chat.deepseek.com/");

  mainWindow.webContents.on("did-finish-load", () => {
    mainWindow.webContents.executeJavaScript(
      `
      const { ipcRenderer } = require('electron');
      
      function extractDivContent(element) {
        let result = '';
        
        if (element.nodeName === 'DIV') {            
            result += element.textContent.trim() + ' ';
        }
        
        for (const child of element.children) {
          result += extractDivContent(child) + ' ';
        }

         return result;
      }

    const targetNode = document.body; 
      
    const config = {        
        childList: true, 
        subtree: true, 
    };
      
      const callback = (mutationsList, observer) => {
          for (const mutation of mutationsList) {
              if (mutation.type === 'childList') {
                  // Check if any nodes were added
                  mutation.addedNodes.forEach(node => {                                 
                      if (node.nodeName === 'DIV' && node.matches('.ds-flex')) {                         
                        const parentElement = node.parentElement;                        
                        const filteredChildren = parentElement.querySelectorAll('div.ds-markdown.ds-markdown--block');
                        if (filteredChildren.length > 0) {
                          const first = filteredChildren[0];
                          const content = extractDivContent(first);
                          console.log(content);

                          ipcRenderer.invoke('reply-arrived', content);
                        }
                      }
                  });
              } 
          }
      };
      
      const observer = new MutationObserver(callback);      
      observer.observe(targetNode, config);


    `,
    );
  });

  const wss = new WebSocketServer({ port: 8080 });

  wss.on('connection', (ws) => {
    console.log('New client connected!');
  
    ipcMain.removeAllListeners("reply-arrived");
    ipcMain.handle("reply-arrived", (event, message) => {
      ws.send(`${message}`);    
    });  

    ws.on('message', (message) => {
      console.log(`Received message: ${message.toString()}`);
      
      mainWindow.webContents.executeJavaScript('document.getElementById("chat-input").focus()');

      setTimeout(() => {
        mainWindow.webContents.sendInputEvent({
          type: 'char',
          keyCode: ' '
        })

        for(var letter of message.toString()) {
          mainWindow.webContents.sendInputEvent({
            type: 'char',
            keyCode: letter
          })
        }
      
        mainWindow.webContents.sendInputEvent({
          type: 'keyDown',
          keyCode: 'Enter'
        })
      }, 100);

    });
  
    ws.on('close', () => {
      console.log('Client disconnected');
    });
  });
};

app.whenReady().then(() => {
  createWindow();
});