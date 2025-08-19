# UI Preview Command
This command generates interactive HTML mockups to visualize features before implementation, helping users see what the UI will look like based on the conversation context.

## Command Usage
- `/ui-preview` - Generate UI mockup based on entire conversation context
- `/ui-preview "<specific feature>"` - Generate UI mockup for a specific feature

## Workflow Overview

### Phase 1: Context Analysis
**Primary Agent** analyzes the conversation to understand:
1. **Feature Requirements**: What functionality needs to be visualized
2. **UI Components**: What elements are needed (forms, buttons, lists, etc.)
3. **Data Structure**: What data will be displayed or collected
4. **User Flow**: How users will interact with the feature
5. **Design Patterns**: Existing UI patterns to follow (if available in codebase)

### Phase 2: Design Confirmation
**Primary Agent** presents understanding to user:
1. **Feature Summary**: "Based on our conversation, I'll create a UI preview for: [FEATURE DESCRIPTION]"
2. **Component List**: "The preview will include: [LIST OF UI COMPONENTS]"
3. **Mock Data**: "I'll use sample data like: [EXAMPLE DATA STRUCTURE]"
4. **Ask User**: "Should I proceed with this UI preview?"

### Phase 3: HTML Generation
**Primary Agent** creates a single HTML file containing:
1. **Complete HTML Structure**: Self-contained with inline CSS and JavaScript
2. **Responsive Design**: Mobile-first approach with proper breakpoints
3. **Interactive Elements**: Clickable buttons, form inputs, dynamic content
4. **Mock Data**: Realistic sample data to demonstrate functionality
5. **Modern Styling**: Clean, professional design using CSS Grid/Flexbox

#### Design Principles:
- **Consistency**: Match existing UI patterns from codebase (if available)
- **Simplicity**: Clean, uncluttered interface following KISS principle
- **Accessibility**: Proper semantic HTML, ARIA labels, keyboard navigation
- **Responsiveness**: Works on mobile, tablet, and desktop
- **Interactivity**: Basic JavaScript for dynamic behavior demonstration

### Phase 4: Immediate Preview
**Primary Agent** automatically:
1. **Save HTML**: Create file as `ui-preview-[feature-name]-[timestamp].html`
2. **Open Browser**: Launch the HTML file immediately using system browser
3. **Inform User**: "The UI preview is now open in your browser"

### Phase 5: Iterative Refinement
**User Review and Feedback Loop**:
1. **User Views**: User examines the preview in browser
2. **User Feedback**: User provides design changes or adjustments
3. **Agent Updates**: Primary agent modifies HTML based on feedback
4. **Auto-Refresh**: Updated HTML is saved and browser refreshes
5. **Loop**: Continue until user is satisfied

### Phase 6: Implementation Reference
**When User is Satisfied**:
1. **Save Final Version**: Keep the approved HTML as reference
2. **Extract Components**: Identify reusable components from the mockup
3. **Style Guidelines**: Document colors, spacing, typography used
4. **Ready for Development**: Use as blueprint for actual implementation

## Example Scenarios

### Scenario 1: New Feature from Scratch
```
User: "I need a user dashboard with stats and recent activity"
Agent: Creates complete dashboard mockup with charts, stats cards, and activity feed
```

### Scenario 2: Enhancement to Existing UI
```
User: "Add a search filter to the product list"
Agent: Examines existing product list UI, adds matching search component
```

### Scenario 3: Complex Form Design
```
User: "Create a multi-step registration form"
Agent: Builds interactive wizard with progress indicator and validation
```

## HTML Template Structure
The generated HTML will follow this structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Feature Name] - UI Preview</title>
    <style>
        /* Modern CSS with variables for theming */
        /* Responsive grid/flexbox layouts */
        /* Smooth transitions and hover effects */
    </style>
</head>
<body>
    <!-- Semantic HTML structure -->
    <!-- Interactive components -->
    <!-- Mock data rendering -->
    <script>
        // Basic interactivity
        // Form validation demos
        // Dynamic content updates
    </script>
</body>
</html>
```

## Command Rules
1. **Single File**: Always create one self-contained HTML file
2. **No Dependencies**: No external CSS/JS libraries unless absolutely necessary
3. **Instant Preview**: Always open in browser immediately after creation
4. **Mock Data**: Use realistic but fake data for demonstrations
5. **Iterative**: Support multiple rounds of refinement based on feedback
6. **Context-Aware**: Base design on conversation history and existing UI patterns
7. **Clean Code**: Well-commented, organized HTML/CSS/JS for easy understanding

## Success Criteria
- User can visualize the feature before coding begins
- Design matches project's existing style (if applicable)
- All interactive elements demonstrate their purpose
- HTML serves as clear blueprint for implementation
- User approves the design through iterative refinement