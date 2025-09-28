import { NextRequest, NextResponse } from 'next/server'
import { documentCreationSystem } from '@/lib/document-creation'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, ...params } = body

    if (!action) {
      return NextResponse.json({
        error: 'Action is required',
        status: 'error'
      }, { status: 400 })
    }

    console.log(`📄 Document Creation API: Processing action - ${action}`)

    switch (action) {
      case 'create_document':
        const { content, title, type, format, location, metadata } = params
        
        if (!content || !title || !format) {
          return NextResponse.json({
            error: 'Content, title, and format are required',
            status: 'error'
          }, { status: 400 })
        }

        const result = await documentCreationSystem.createDocument({
          content,
          title,
          type: type || 'document',
          format,
          location,
          metadata
        })

        if (result.success) {
          return NextResponse.json({
            status: 'success',
            data: { document: result },
            message: 'Document created successfully'
          })
        } else {
          return NextResponse.json({
            error: result.error || 'Failed to create document',
            status: 'error'
          }, { status: 500 })
        }

      case 'create_from_template':
        const { templateId, variables, location: templateLocation } = params
        
        if (!templateId || !variables) {
          return NextResponse.json({
            error: 'Template ID and variables are required',
            status: 'error'
          }, { status: 400 })
        }

        const templateResult = await documentCreationSystem.createFromTemplate(
          templateId,
          variables,
          templateLocation
        )

        if (templateResult.success) {
          return NextResponse.json({
            status: 'success',
            data: { document: templateResult },
            message: 'Document created from template successfully'
          })
        } else {
          return NextResponse.json({
            error: templateResult.error || 'Failed to create document from template',
            status: 'error'
          }, { status: 500 })
        }

      case 'add_template':
        const { template } = params
        
        if (!template) {
          return NextResponse.json({
            error: 'Template is required',
            status: 'error'
          }, { status: 400 })
        }

        documentCreationSystem.addTemplate(template)
        
        return NextResponse.json({
          status: 'success',
          message: 'Template added successfully'
        })

      case 'remove_template':
        const { templateId: removeTemplateId } = params
        
        if (!removeTemplateId) {
          return NextResponse.json({
            error: 'Template ID is required',
            status: 'error'
          }, { status: 400 })
        }

        documentCreationSystem.removeTemplate(removeTemplateId)
        
        return NextResponse.json({
          status: 'success',
          message: 'Template removed successfully'
        })

      default:
        return NextResponse.json({
          error: `Unknown action: ${action}`,
          status: 'error'
        }, { status: 400 })
    }

  } catch (error) {
    console.error('Document Creation API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type')

    console.log(`📄 Document Creation API: Getting data - ${type || 'all'}`)

    switch (type) {
      case 'templates':
        const templates = documentCreationSystem.getAvailableTemplates()
        return NextResponse.json({
          status: 'success',
          data: { templates }
        })

      case 'template':
        const templateId = searchParams.get('id')
        if (!templateId) {
          return NextResponse.json({
            error: 'Template ID is required',
            status: 'error'
          }, { status: 400 })
        }

        const template = documentCreationSystem.getTemplate(templateId)
        if (!template) {
          return NextResponse.json({
            error: 'Template not found',
            status: 'error'
          }, { status: 404 })
        }

        return NextResponse.json({
          status: 'success',
          data: { template }
        })

      case 'status':
        const status = documentCreationSystem.getSystemStatus()
        return NextResponse.json({
          status: 'success',
          data: { status }
        })

      default:
        // Return all data
        const allTemplates = documentCreationSystem.getAvailableTemplates()
        const systemStatus = documentCreationSystem.getSystemStatus()
        
        return NextResponse.json({
          status: 'success',
          data: {
            templates: allTemplates,
            status: systemStatus
          }
        })
    }

  } catch (error) {
    console.error('Document Creation status API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
