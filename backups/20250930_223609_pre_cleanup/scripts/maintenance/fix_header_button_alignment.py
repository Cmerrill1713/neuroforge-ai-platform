#!/usr/bin/env python3
""'
Header and Button Alignment Fix Script
Fix alignment issues in header, toolbar, and buttons
""'

import os
import re
from pathlib import Path
from typing import Dict, List, Any

class HeaderButtonAlignmentFixer:
    """TODO: Add docstring."""
    """Fix header and button alignment issues.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.frontend_dir = Path("frontend')
        self.components_dir = self.frontend_dir / "src" / "components'
        self.app_dir = self.frontend_dir / "app'

    def fix_all_alignment(self):
        """TODO: Add docstring."""
        """Fix header and button alignment in all components.""'
        print("🔧 Fixing Header and Button Alignment Issues...')

        # Fix main page header and buttons
        self.fix_main_page_alignment()

        # Fix component headers and buttons
        self.fix_component_headers()
        self.fix_component_buttons()

        print("✅ Header and button alignment fixes completed!')

    def fix_main_page_alignment(self):
        """TODO: Add docstring."""
        """Fix main page header and button alignment.""'
        print("🔧 Fixing main page alignment...')

        main_page = self.app_dir / "page.tsx'
        if not main_page.exists():
            return

        content = main_page.read_text()

        # Fix AppBar alignment
        content = re.sub(
            r"<Toolbar>',
            "<Toolbar sx={{ minHeight: \"64px !important\", alignItems: \"center\", justifyContent: \"space-between\" }}>',
            content
        )

        # Fix header title alignment
        content = re.sub(
            r"<Box sx=\{\{ flexGrow: 1 \}\}>',
            "<Box sx={{ flexGrow: 1, display: \"flex\", alignItems: \"center\", justifyContent: \"flex-start\" }}>',
            content
        )

        # Fix header button stack alignment
        content = re.sub(
            r"<Stack direction="row" spacing=\{1\} alignItems="center">',
            "<Stack direction="row" spacing={{ xs: 0.5, sm: 1, md: 1.5 }} alignItems="center" justifyContent="flex-end">',
            content
        )

        # Fix IconButton alignment in header
        content = re.sub(
            r"sx=\{\{ mr: 2 \}\}',
            "sx={{ mr: { xs: 1, sm: 2 }, alignSelf: \"center\" }}',
            content
        )

        # Fix Avatar alignment
        content = re.sub(
            r"sx=\{\{\s*mr: 2,',
            "sx={{\n                mr: { xs: 1, sm: 2 },\n                alignSelf: \"center\",',
            content
        )

        # Fix Performance Monitor alignment
        content = re.sub(
            r"justifyContent="center"',
            "justifyContent={{ xs: \"space-around\", sm: \"center\" }}',
            content
        )

        # Fix Performance Monitor spacing
        content = re.sub(
            r"spacing=\{4\}',
            "spacing={{ xs: 2, sm: 3, md: 4 }}',
            content
        )

        # Fix Performance Monitor padding
        content = re.sub(
            r"sx=\{\{ px: 2 \}\}',
            "sx={{ px: { xs: 1, sm: 2, md: 3 } }}',
            content
        )

        # Fix FAB alignment
        content = re.sub(
            r"bottom: 24,\s*right: 24,',
            "bottom: { xs: 16, sm: 24 },\n              right: { xs: 16, sm: 24 },',
            content
        )

        main_page.write_text(content)
        print("✅ Fixed main page header and button alignment')

    def fix_component_headers(self):
        """TODO: Add docstring."""
        """Fix component header alignment.""'
        print("🔧 Fixing component headers...')

        components = [
            "AdvancedChatFeatures.tsx',
            "VoiceIntegration.tsx',
            "RealTimeCollaboration.tsx',
            "LearningDashboard.tsx',
            "MultimodalPanel.tsx',
            "CodeEditor.tsx',
            "MuiEnhancedChatPanel.tsx'
        ]

        for component_name in components:
            component = self.components_dir / component_name
            if not component.exists():
                continue

            content = component.read_text()

            # Fix header alignment patterns
            content = re.sub(
                r"<Box sx=\{\{\s*display:\s*[\""]flex[\""],\s*alignItems:\s*[\""]center[\""],\s*mb:\s*\d+',
                "<Box sx={{\n        display: \"flex\",\n        alignItems: \"center\",\n        justifyContent: \"space-between\",\n        mb: { xs: 2, sm: 3, md: 4 },',
                content
            )

            # Fix header title alignment
            content = re.sub(
                r"<Typography variant="h6"',
                "<Typography variant="h6" sx={{ alignSelf: \"center\" }}',
                content
            )

            # Fix header button alignment
            content = re.sub(
                r"<IconButton[^>]*>',
                lambda m: m.group(0).replace(">", " sx={{ alignSelf: \"center\" }}>'),
                content
            )

            component.write_text(content)
            print(f"✅ Fixed {component_name} header alignment')

    def fix_component_buttons(self):
        """TODO: Add docstring."""
        """Fix component button alignment.""'
        print("🔧 Fixing component buttons...')

        components = [
            "AdvancedChatFeatures.tsx',
            "VoiceIntegration.tsx',
            "RealTimeCollaboration.tsx',
            "LearningDashboard.tsx',
            "MultimodalPanel.tsx',
            "CodeEditor.tsx',
            "MuiEnhancedChatPanel.tsx'
        ]

        for component_name in components:
            component = self.components_dir / component_name
            if not component.exists():
                continue

            content = component.read_text()

            # Fix button stack alignment
            content = re.sub(
                r"<Stack direction="row" spacing=\{1\}',
                "<Stack direction="row" spacing={{ xs: 0.5, sm: 1, md: 1.5 }} alignItems="center" justifyContent="center"',
                content
            )

            # Fix button alignment in forms
            content = re.sub(
                r"<Button[^>]*variant="contained"',
                lambda m: m.group(0) + " sx={{ alignSelf: \"center\", minWidth: { xs: \"auto\", sm: \"120px\" } }}',
                content
            )

            # Fix IconButton alignment
            content = re.sub(
                r"<IconButton[^>]*color="primary"',
                lambda m: m.group(0) + " sx={{ alignSelf: \"center\" }}',
                content
            )

            # Fix input area button alignment
            content = re.sub(
                r"sx=\{\{\s*display:\s*[\""]flex[\""],\s*gap:\s*\d+',
                "sx={{\n        display: \"flex\",\n        alignItems: \"center\",\n        gap: { xs: 1, sm: 1.5, md: 2 },',
                content
            )

            component.write_text(content)
            print(f"✅ Fixed {component_name} button alignment')

    def create_alignment_utilities(self):
        """TODO: Add docstring."""
        """Create alignment utility classes.""'
        print("🔧 Creating alignment utilities...')

        # Create alignment utilities file
        utils_dir = self.frontend_dir / "src" / "utils'
        utils_dir.mkdir(exist_ok=True)

        alignment_utils = utils_dir / "alignment.ts'

        content = ""'
// Alignment utility functions and styles
export const alignmentStyles = {
  // Header alignment
  headerContainer: {
    display: "flex',
    alignItems: "center',
    justifyContent: "space-between',
    minHeight: "64px',
    px: { xs: 2, sm: 3, md: 4 },
    py: { xs: 1, sm: 1.5, md: 2 }
  },

  // Button alignment
  buttonStack: {
    display: "flex',
    alignItems: "center',
    justifyContent: "center',
    gap: { xs: 0.5, sm: 1, md: 1.5 }
  },

  // Form alignment
  formContainer: {
    display: "flex',
    flexDirection: "column',
    alignItems: "center',
    gap: { xs: 1.5, sm: 2, md: 2.5 }
  },

  // Content alignment
  contentContainer: {
    display: "flex',
    alignItems: "center',
    justifyContent: "center',
    minHeight: "100%'
  },

  // Responsive alignment
  responsiveAlignment: {
    xs: "center',
    sm: "flex-start',
    md: "flex-start'
  }
}

// Alignment helper functions
export const getAlignmentProps = (breakpoint: "xs" | "sm" | "md" | "lg" | "xl" = "md') => ({
  alignItems: alignmentStyles.responsiveAlignment[breakpoint] || "center',
  justifyContent: "center'
})

// Button alignment props
export const getButtonAlignmentProps = () => ({
  alignSelf: "center',
  minWidth: { xs: "auto", sm: "120px' },
  height: { xs: "36px", sm: "40px", md: "44px' }
})

// Header alignment props
export const getHeaderAlignmentProps = () => ({
  display: "flex',
  alignItems: "center',
  justifyContent: "space-between',
  minHeight: "64px',
  px: { xs: 2, sm: 3, md: 4 },
  py: { xs: 1, sm: 1.5, md: 2 }
})
""'

        alignment_utils.write_text(content)
        print("✅ Created alignment utilities')

    def fix_toolbar_alignment(self):
        """TODO: Add docstring."""
        """Fix toolbar alignment specifically.""'
        print("🔧 Fixing toolbar alignment...')

        main_page = self.app_dir / "page.tsx'
        if not main_page.exists():
            return

        content = main_page.read_text()

        # Fix toolbar min height and alignment
        content = re.sub(
            r"<Toolbar[^>]*>',
            "<Toolbar sx={{ minHeight: \"64px !important\", alignItems: \"center\", justifyContent: \"space-between\", px: { xs: 1, sm: 2, md: 3 } }}>',
            content
        )

        # Fix toolbar content alignment
        content = re.sub(
            r"<Box sx=\{\{ flexGrow: 1 \}\}>',
            "<Box sx={{ flexGrow: 1, display: \"flex\", alignItems: \"center\", justifyContent: \"flex-start\", minHeight: \"64px\" }}>',
            content
        )

        # Fix toolbar right side alignment
        content = re.sub(
            r"<Stack direction="row" spacing=\{1\} alignItems="center">',
            "<Stack direction="row" spacing={{ xs: 0.5, sm: 1, md: 1.5 }} alignItems="center" justifyContent="flex-end" sx={{ minHeight: \"64px\" }}>',
            content
        )

        main_page.write_text(content)
        print("✅ Fixed toolbar alignment')

def main():
    """TODO: Add docstring."""
    """Main function.""'
    print("🔧 Header and Button Alignment Fixer')
    print("=' * 50)

    fixer = HeaderButtonAlignmentFixer()
    fixer.fix_all_alignment()
    fixer.create_alignment_utilities()
    fixer.fix_toolbar_alignment()

    print("\n✅ Header and button alignment fixes completed!')
    print("\n📋 Improvements made:')
    print("• Fixed AppBar and Toolbar alignment')
    print("• Improved header button spacing and alignment')
    print("• Enhanced Performance Monitor alignment')
    print("• Fixed component header alignment')
    print("• Improved button stack alignment')
    print("• Added responsive alignment system')
    print("• Created alignment utility functions')

    print("\n🎯 Next steps:')
    print("1. Test header alignment on different screen sizes')
    print("2. Verify button alignment in all components')
    print("3. Check toolbar alignment and spacing')
    print("4. Test responsive behavior')

if __name__ == "__main__':
    main()
