import { useState, useCallback } from 'react';

interface UseCopyReturn {
  isCopied: boolean;
  copyToClipboard: (text: string) => Promise<boolean>;
  copyMessage: (message: string) => Promise<boolean>;
  copyCodeBlock: (code: string, language?: string) => Promise<boolean>;
}

export const useCopy = (): UseCopyReturn => {
  const [isCopied, setIsCopied] = useState(false);

  const copyToClipboard = useCallback(async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
        return true;
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          setIsCopied(true);
          setTimeout(() => setIsCopied(false), 2000);
        }
        
        return successful;
      }
    } catch (error) {
      console.error('Failed to copy text:', error);
      return false;
    }
  }, []);

  const copyMessage = useCallback(async (message: string): Promise<boolean> => {
    return copyToClipboard(message);
  }, [copyToClipboard]);

  const copyCodeBlock = useCallback(async (code: string, language?: string): Promise<boolean> => {
    const formattedCode = language ? `\`\`\`${language}\n${code}\n\`\`\`` : code;
    return copyToClipboard(formattedCode);
  }, [copyToClipboard]);

  return {
    isCopied,
    copyToClipboard,
    copyMessage,
    copyCodeBlock,
  };
};
