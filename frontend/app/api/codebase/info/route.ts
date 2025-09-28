import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    // In production, you would fetch real codebase information
    // For now, we'll return mock data with some real system info
    
    const codebaseInfo = {
      name: 'AI Studio Enhanced',
      path: '/Users/christianmerrill/Prompt Engineering/frontend',
      branch: 'main',
      lastCommit: '2 hours ago',
      connected: true,
      fileCount: 1247,
      totalSize: '2.3 MB',
      lastSync: new Date().toISOString(),
    };

    // Try to get real git info if available
    try {
      const { stdout: branchOutput } = await execAsync('git branch --show-current');
      const { stdout: lastCommitOutput } = await execAsync('git log -1 --format="%h %s" --date=relative');
      
      codebaseInfo.branch = branchOutput.trim();
      codebaseInfo.lastCommit = lastCommitOutput.trim();
    } catch (gitError) {
      // Git not available or not a git repository, use defaults
      console.log('Git info not available, using defaults');
    }

    return NextResponse.json({
      success: true,
      codebase: codebaseInfo,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Error fetching codebase info:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch codebase info' },
      { status: 500 }
    );
  }
}
