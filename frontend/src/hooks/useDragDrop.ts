import { useState, useCallback, useRef } from 'react';

interface DragDropItem {
  id: string;
  name: string;
  type: string;
  size: number;
  content: string | ArrayBuffer;
  file?: File;
}

interface UseDragDropReturn {
  isDragOver: boolean;
  droppedItems: DragDropItem[];
  handleDragOver: (e: React.DragEvent) => void;
  handleDragLeave: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => void;
  clearItems: () => void;
  removeItem: (id: string) => void;
}

export const useDragDrop = (): UseDragDropReturn => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [droppedItems, setDroppedItems] = useState<DragDropItem[]>([]);
  const dragCounterRef = useRef(0);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current++;
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current--;
    if (dragCounterRef.current === 0) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    dragCounterRef.current = 0;

    const files = Array.from(e.dataTransfer.files);
    const newItems: DragDropItem[] = [];

    for (const file of files) {
      try {
        const item: DragDropItem = {
          id: `${Date.now()}-${Math.random()}`,
          name: file.name,
          type: file.type,
          size: file.size,
          file: file,
          content: await readFileContent(file),
        };
        newItems.push(item);
      } catch (error) {
        console.error('Error reading file:', error);
      }
    }

    // Handle text content from drag
    const textContent = e.dataTransfer.getData('text/plain');
    if (textContent && !files.length) {
      const item: DragDropItem = {
        id: `${Date.now()}-${Math.random()}`,
        name: 'Text Content',
        type: 'text/plain',
        size: textContent.length,
        content: textContent,
      };
      newItems.push(item);
    }

    setDroppedItems(prev => [...prev, ...newItems]);
  }, []);

  const readFileContent = async (file: File): Promise<string | ArrayBuffer> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = () => {
        resolve(reader.result as string | ArrayBuffer);
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      if (file.type.startsWith('text/') || file.type === 'application/json') {
        reader.readAsText(file);
      } else {
        reader.readAsArrayBuffer(file);
      }
    });
  };

  const clearItems = useCallback(() => {
    setDroppedItems([]);
  }, []);

  const removeItem = useCallback((id: string) => {
    setDroppedItems(prev => prev.filter(item => item.id !== id));
  }, []);

  return {
    isDragOver,
    droppedItems,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    clearItems,
    removeItem,
  };
};
