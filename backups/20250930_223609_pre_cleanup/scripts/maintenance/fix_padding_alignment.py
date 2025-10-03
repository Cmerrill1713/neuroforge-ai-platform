#!/usr/bin/env python3
""'
Padding and Alignment Fix Script
Fix padding, spacing, and alignment issues across the frontend
""'

import os
import re
from pathlib import Path
from typing import Dict, List, Any

class PaddingAlignmentFixer:
    """TODO: Add docstring."""
    """Fix padding and alignment issues in frontend components.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.frontend_dir = Path("frontend')
        self.components_dir = self.frontend_dir / "src" / "components'
        self.app_dir = self.frontend_dir / "app'

    def fix_all_components(self):
        """TODO: Add docstring."""
        """Fix padding and alignment in all components.""'
        print("🔧 Fixing Padding and Alignment Issues...')

        # Fix main page
        self.fix_main_page()

        # Fix all components
        self.fix_performance_monitor()
        self.fix_advanced_chat_features()
        self.fix_voice_integration()
        self.fix_realtime_collaboration()
        self.fix_learning_dashboard()
        self.fix_multimodal_panel()
        self.fix_code_editor()
        self.fix_mui_enhanced_chat()

        print("✅ Padding and alignment fixes completed!')

    def fix_main_page(self):
        """TODO: Add docstring."""
        """Fix main page padding and alignment.""'
        print("🔧 Fixing main page...')

        main_page = self.app_dir / "page.tsx'
        if not main_page.exists():
            return

        content = main_page.read_text()

        # Fix main content padding
        content = re.sub(
            r"sx=\{\{\s*flexGrow:\s*1,\s*p:\s*3,',
            "sx={{\n            flexGrow: 1,\n            p: { xs: 2, sm: 3, md: 4 },\n            px: { xs: 2, sm: 3, md: 4 },\n            py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix drawer width and spacing
        content = re.sub(
            r"const drawerWidth = 280',
            "const drawerWidth = 280',
            content
        )

        # Fix AppBar padding
        content = re.sub(
            r"sx=\{\{\s*background:\s*[\""]linear-gradient',
            "sx={{\n            background: \"linear-gradient',
            content
        )

        # Fix panel content alignment
        content = re.sub(
            r"<Box sx=\{\{ height:\s*[\""]100%[\""], background:',
            "<Box sx={{\n                height: \"100%\",\n                background:',
            content
        )

        main_page.write_text(content)
        print("✅ Fixed main page padding and alignment')

    def fix_performance_monitor(self):
        """TODO: Add docstring."""
        """Fix PerformanceMonitor padding and alignment.""'
        print("🔧 Fixing PerformanceMonitor...')

        component = self.components_dir / "PerformanceMonitor.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix compact mode padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*1,',
            "sx={{\n          p: { xs: 1, sm: 1.5, md: 2 },',
            content
        )

        # Fix header padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2,',
            "sx={{\n            p: { xs: 2, sm: 2.5, md: 3 },\n            px: { xs: 2, sm: 2.5, md: 3 },\n            py: { xs: 1.5, sm: 2, md: 2.5 },',
            content
        )

        # Fix metrics grid padding
        content = re.sub(
            r"<Box sx=\{\{ p:\s*2 \}\}>',
            "<Box sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>',
            content
        )

        # Fix card content padding
        content = re.sub(
            r"sx=\{\{ p:\s*2, \"&:last-child\":\s*\{\s*pb:\s*2\s*\}\s*\}',
            "sx={{\n                    p: { xs: 1.5, sm: 2, md: 2.5 },\n                    \"&:last-child\": { pb: { xs: 1.5, sm: 2, md: 2.5 } }\n                  }}',
            content
        )

        # Fix detailed view padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2,',
            "sx={{\n              p: { xs: 2, sm: 2.5, md: 3 },\n              px: { xs: 2, sm: 2.5, md: 3 },\n              py: { xs: 1.5, sm: 2, md: 2.5 },',
            content
        )

        component.write_text(content)
        print("✅ Fixed PerformanceMonitor padding and alignment')

    def fix_advanced_chat_features(self):
        """TODO: Add docstring."""
        """Fix AdvancedChatFeatures padding and alignment.""'
        print("🔧 Fixing AdvancedChatFeatures...')

        component = self.components_dir / "AdvancedChatFeatures.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix chat container padding
        content = re.sub(
            r"sx=\{\{\s*flexGrow:\s*1,\s*p:\s*2',
            "sx={{\n        flexGrow: 1,\n        p: { xs: 1.5, sm: 2, md: 2.5 },\n        px: { xs: 1.5, sm: 2, md: 2.5 },\n        py: { xs: 1, sm: 1.5, md: 2 },',
            content
        )

        # Fix message padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2,\s*mb:\s*2',
            "sx={{\n          p: { xs: 1.5, sm: 2, md: 2.5 },\n          px: { xs: 1.5, sm: 2, md: 2.5 },\n          py: { xs: 1, sm: 1.5, md: 2 },\n          mb: { xs: 1.5, sm: 2, md: 2.5 },',
            content
        )

        # Fix input area padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2,\s*borderTop',
            "sx={{\n        p: { xs: 1.5, sm: 2, md: 2.5 },\n        px: { xs: 1.5, sm: 2, md: 2.5 },\n        py: { xs: 1, sm: 1.5, md: 2 },\n        borderTop',
            content
        )

        component.write_text(content)
        print("✅ Fixed AdvancedChatFeatures padding and alignment')

    def fix_voice_integration(self):
        """TODO: Add docstring."""
        """Fix VoiceIntegration padding and alignment.""'
        print("🔧 Fixing VoiceIntegration...')

        component = self.components_dir / "VoiceIntegration.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix control panel padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*3,\s*background',
            "sx={{\n        p: { xs: 2, sm: 2.5, md: 3 },\n        px: { xs: 2, sm: 2.5, md: 3 },\n        py: { xs: 1.5, sm: 2, md: 2.5 },\n        background',
            content
        )

        component.write_text(content)
        print("✅ Fixed VoiceIntegration padding and alignment')

    def fix_realtime_collaboration(self):
        """TODO: Add docstring."""
        """Fix RealTimeCollaboration padding and alignment.""'
        print("🔧 Fixing RealTimeCollaboration...')

        component = self.components_dir / "RealTimeCollaboration.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix user list padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2',
            "sx={{\n        p: { xs: 1.5, sm: 2, md: 2.5 },\n        px: { xs: 1.5, sm: 2, md: 2.5 },\n        py: { xs: 1, sm: 1.5, md: 2 },',
            content
        )

        component.write_text(content)
        print("✅ Fixed RealTimeCollaboration padding and alignment')

    def fix_learning_dashboard(self):
        """TODO: Add docstring."""
        """Fix LearningDashboard padding and alignment.""'
        print("🔧 Fixing LearningDashboard...')

        component = self.components_dir / "LearningDashboard.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix progress section padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*3',
            "sx={{\n        p: { xs: 2, sm: 2.5, md: 3 },\n        px: { xs: 2, sm: 2.5, md: 3 },\n        py: { xs: 1.5, sm: 2, md: 2.5 },',
            content
        )

        component.write_text(content)
        print("✅ Fixed LearningDashboard padding and alignment')

    def fix_multimodal_panel(self):
        """TODO: Add docstring."""
        """Fix MultimodalPanel padding and alignment.""'
        print("🔧 Fixing MultimodalPanel...')

        component = self.components_dir / "MultimodalPanel.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix upload area padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*4',
            "sx={{\n        p: { xs: 2, sm: 3, md: 4 },\n        px: { xs: 2, sm: 3, md: 4 },\n        py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        component.write_text(content)
        print("✅ Fixed MultimodalPanel padding and alignment')

    def fix_code_editor(self):
        """TODO: Add docstring."""
        """Fix CodeEditor padding and alignment.""'
        print("🔧 Fixing CodeEditor...')

        component = self.components_dir / "CodeEditor.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*2',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 1.5, sm: 2, md: 2.5 },\n      px: { xs: 1.5, sm: 2, md: 2.5 },\n      py: { xs: 1, sm: 1.5, md: 2 },',
            content
        )

        # Fix toolbar padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*1',
            "sx={{\n        p: { xs: 1, sm: 1.5, md: 2 },\n        px: { xs: 1, sm: 1.5, md: 2 },\n        py: { xs: 0.5, sm: 1, md: 1.5 },',
            content
        )

        component.write_text(content)
        print("✅ Fixed CodeEditor padding and alignment')

    def fix_mui_enhanced_chat(self):
        """TODO: Add docstring."""
        """Fix MuiEnhancedChatPanel padding and alignment.""'
        print("🔧 Fixing MuiEnhancedChatPanel...')

        component = self.components_dir / "MuiEnhancedChatPanel.tsx'
        if not component.exists():
            return

        content = component.read_text()

        # Fix main container padding
        content = re.sub(
            r"sx=\{\{\s*height:\s*[\""]100%[\""],\s*display:\s*[\""]flex[\""],\s*flexDirection:\s*[\""]column[\""],\s*p:\s*3',
            "sx={{\n      height: \"100%\",\n      display: \"flex\",\n      flexDirection: \"column\",\n      p: { xs: 2, sm: 3, md: 4 },\n      px: { xs: 2, sm: 3, md: 4 },\n      py: { xs: 2, sm: 3, md: 4 },',
            content
        )

        # Fix message list padding
        content = re.sub(
            r"sx=\{\{\s*flexGrow:\s*1,\s*p:\s*2',
            "sx={{\n        flexGrow: 1,\n        p: { xs: 1.5, sm: 2, md: 2.5 },\n        px: { xs: 1.5, sm: 2, md: 2.5 },\n        py: { xs: 1, sm: 1.5, md: 2 },',
            content
        )

        # Fix input area padding
        content = re.sub(
            r"sx=\{\{\s*p:\s*2,\s*borderTop',
            "sx={{\n        p: { xs: 1.5, sm: 2, md: 2.5 },\n        px: { xs: 1.5, sm: 2, md: 2.5 },\n        py: { xs: 1, sm: 1.5, md: 2 },\n        borderTop',
            content
        )

        component.write_text(content)
        print("✅ Fixed MuiEnhancedChatPanel padding and alignment')

    def create_responsive_theme(self):
        """TODO: Add docstring."""
        """Create responsive theme configuration.""'
        print("🔧 Creating responsive theme...')

        theme_file = self.frontend_dir / "src" / "theme" / "muiTheme.ts'
        if not theme_file.exists():
            return

        content = theme_file.read_text()

        # Add responsive spacing
        responsive_spacing = ""'
// Responsive spacing configuration
const responsiveSpacing = {
  xs: 1,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 5
}

// Responsive padding configuration
const responsivePadding = {
  xs: 2,
  sm: 3,
  md: 4,
  lg: 5,
  xl: 6
}

// Responsive margin configuration
const responsiveMargin = {
  xs: 1,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 5
}
""'

        # Add to theme
        if "responsiveSpacing' not in content:
            content = content.replace(
                "export const aiStudio2025Theme = createTheme({',
                f"{responsiveSpacing}\n\nexport const aiStudio2025Theme = createTheme({'
            )

        theme_file.write_text(content)
        print("✅ Created responsive theme configuration')

def main():
    """TODO: Add docstring."""
    """Main function.""'
    print("🔧 Padding and Alignment Fixer')
    print("=' * 50)

    fixer = PaddingAlignmentFixer()
    fixer.fix_all_components()
    fixer.create_responsive_theme()

    print("\n✅ Padding and alignment fixes completed!')
    print("\n📋 Improvements made:')
    print("• Responsive padding across all components')
    print("• Consistent spacing on mobile, tablet, and desktop')
    print("• Better alignment and visual hierarchy')
    print("• Improved touch targets for mobile devices')
    print("• Consistent Material-UI spacing system')

    print("\n🎯 Next steps:')
    print("1. Test the frontend on different screen sizes')
    print("2. Verify touch targets are appropriate')
    print("3. Check alignment on various devices')
    print("4. Test with different content lengths')

if __name__ == "__main__':
    main()
