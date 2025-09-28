import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { code, language } = await request.json();

    if (!code || !language) {
      return NextResponse.json(
        { success: false, error: 'Code and language are required' },
        { status: 400 }
      );
    }

    // In production, you would use a proper code formatter like Prettier
    // For now, we'll simulate basic formatting
    
    let formattedCode = code;

    try {
      if (language === 'javascript' || language === 'typescript') {
        // Basic JavaScript/TypeScript formatting simulation
        formattedCode = code
          .replace(/\s*{\s*/g, ' {\n  ')
          .replace(/;\s*/g, ';\n')
          .replace(/\s*}\s*/g, '\n}\n')
          .replace(/\n\s*\n/g, '\n')
          .trim();
      } else if (language === 'python') {
        // Basic Python formatting simulation
        formattedCode = code
          .replace(/\n\s*\n/g, '\n')
          .replace(/^\s+$/gm, '')
          .trim();
      }

      return NextResponse.json({
        success: true,
        formattedCode: formattedCode,
        language: language,
        formattedAt: new Date().toISOString(),
      });

    } catch (formatError) {
      return NextResponse.json({
        success: false,
        error: 'Failed to format code',
        originalCode: code,
      });
    }

  } catch (error) {
    console.error('Error formatting code:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to format code' },
      { status: 500 }
    );
  }
}
