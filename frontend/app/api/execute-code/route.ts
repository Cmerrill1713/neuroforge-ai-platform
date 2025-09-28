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

    // In production, you would execute the code safely using a sandboxed environment
    // For now, we'll simulate code execution with basic validation
    
    let output = '';
    let error = null;

    try {
      // Basic validation and simulation
      if (language === 'javascript') {
        // Simulate JavaScript execution
        if (code.includes('console.log')) {
          output = 'Code executed successfully\nOutput logged to console';
        } else if (code.includes('error') || code.includes('Error')) {
          throw new Error('Simulated error in code');
        } else {
          output = 'Code executed successfully';
        }
      } else if (language === 'python') {
        // Simulate Python execution
        if (code.includes('print')) {
          output = 'Code executed successfully\nOutput printed to console';
        } else if (code.includes('error') || code.includes('Error')) {
          throw new Error('Simulated error in code');
        } else {
          output = 'Code executed successfully';
        }
      } else {
        output = `Code executed successfully in ${language}`;
      }

      // Add execution time simulation
      const executionTime = Math.random() * 0.5 + 0.1; // 0.1 to 0.6 seconds
      output += `\n\nExecution completed in ${executionTime.toFixed(2)}s`;

    } catch (execError) {
      error = execError instanceof Error ? execError.message : 'Unknown execution error';
    }

    return NextResponse.json({
      success: true,
      output: output,
      error: error,
      executionTime: Date.now(),
      language: language,
    });

  } catch (error) {
    console.error('Error executing code:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to execute code' },
      { status: 500 }
    );
  }
}
