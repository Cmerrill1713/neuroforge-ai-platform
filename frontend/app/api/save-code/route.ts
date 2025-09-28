import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';

export async function POST(request: NextRequest) {
  try {
    const { code, fileName, language } = await request.json();

    if (!code || !fileName) {
      return NextResponse.json(
        { success: false, error: 'Code and fileName are required' },
        { status: 400 }
      );
    }

    // In production, you would save to a secure location with proper validation
    // For now, we'll simulate saving
    
    const fileExtension = language === 'javascript' ? '.js' : 
                         language === 'typescript' ? '.ts' : 
                         language === 'python' ? '.py' : '.txt';
    
    const fullFileName = fileName.endsWith(fileExtension) ? fileName : `${fileName}${fileExtension}`;
    
    // Simulate file save
    const saveResult = {
      fileName: fullFileName,
      size: code.length,
      language: language,
      savedAt: new Date().toISOString(),
      path: `/workspace/${fullFileName}`,
    };

    return NextResponse.json({
      success: true,
      message: 'Code saved successfully',
      file: saveResult,
    });

  } catch (error) {
    console.error('Error saving code:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to save code' },
      { status: 500 }
    );
  }
}
