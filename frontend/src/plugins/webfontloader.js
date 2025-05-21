// src/plugins/webfontloader.js
export function loadFonts() {
    const webFontLoader = async () => {
      const webfontloader = await import('webfontloader')
  
      webfontloader.load({
        google: {
          families: ['Noto+Sans+KR:100,300,400,500,700,900&display=swap']
        }
      })
    }
    webFontLoader()
  }
  