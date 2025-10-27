# Test Case Management Page Testing Plan

## Project Context

This document provides a comprehensive testing plan for the Test Case Management page functionality, specifically focusing on the Details, Edit, and Delete buttons. The plan is designed to be complete enough that a new session can pick up and execute testing without needing to rediscover requirements.

**Current Status**: We have successfully implemented system prompt and user instruction functionality for all test cases. The Test Case Management page displays test cases in a table format with action buttons for Details, Edit, and Delete operations.

**Key Missing Fields Identified**: After thorough analysis of the TestCaseDetail.tsx component, this plan now includes comprehensive testing for fields and functionality that were initially missed:

### Critical Missing Fields Added:
- **User Feedback Section**: Rating, category, comment, concern, suggested improvement, feedback date, feedback source
- **Detailed Chunk Metadata**: Publish/effective/expiration dates, chunk type, confidence scores, retrieval ranks
- **Visual UI Components**: Progress bars, colored tags, badges, role indicators
- **Form Validation Details**: Required field indicators, character limits, real-time validation, form state management
- **Advanced Functionality**: Auto-save, unsaved changes warnings, button debouncing, state transitions
- **Accessibility Features**: Keyboard navigation, screen reader support, visual accessibility
- **Cross-Platform Support**: Responsive design, browser compatibility, performance metrics

**Target Page**: Test Case Management page accessible via the main navigation
**Components Under Test**:
- `TestCaseDetail.tsx` (914 lines) - Main component handling all three operations
- Details modal with 5 tabs (Overview, Context, Config, Execution, Analysis)
- Edit mode with form validation and save functionality
- Delete confirmation and removal

## Testing Environment Setup

1. **Backend Server**: Ensure Python backend is running on `http://localhost:8000`
2. **Frontend Server**: Ensure React frontend is running on `http://localhost:3000`
3. **Browser**: Chrome with DevTools enabled (F12)
4. **Test Data**: Mock test cases should be populated in the system

## Pre-Testing Checklist

- [ ] Backend server is running and accessible
- [ ] Frontend server is running and can connect to backend
- [ ] Navigate to Test Case Management page
- [ ] Verify test cases are displayed in the table
- [ ] Open Chrome DevTools (Network tab) for API monitoring

## 1. Details Button Testing

### Objective
Verify detailed test case information displays correctly in modal format with all tabs and data properly rendered.

### Test Scenarios

#### 1.1 Basic Modal Display
**Steps:**
1. Navigate to Test Case Management page
2. Click the Details button on any test case row
3. Observe the modal that opens

**Expected Results:**
- Modal opens with correct test case ID and title in header
- All 5 tabs are visible and clickable: Overview, Context, Config, Execution, Analysis
- Close button (X) is visible and functional
- Modal can be closed by clicking outside, pressing Escape key, or clicking Close button

#### 1.2 Overview Tab Content
**Steps:**
1. Open Details modal for any test case
2. Click on Overview tab (default)

**Expected Results:**
- Test case metadata displays correctly:
  - ID (format: TC-0001, etc.)
  - Name
  - Status (draft, approved, etc.)
  - Owner (email format)
  - Priority (low, medium, high)
- Domain and difficulty fields are populated
- Tags display as colored pills
- Created and updated dates in proper format
- Source session ID is displayed

#### 1.3 Context Tab Content
**Steps:**
1. Open Details modal
2. Click on Context tab

**Expected Results:**
- **Current Query** displays with:
  - Full query text
  - Timestamp (ISO format)
- **Conversation History** shows turn-by-turn dialogue:
  - Turn number (sequential)
  - Role (user/assistant/system)
  - Query text (for user turns)
  - Response text (for assistant turns)
  - Retrieved chunk IDs (for assistant turns)
  - Timestamp for each turn
  - **Colored Role Tags** (blue for user, green for assistant, default for system)
- **Current Retrieved Chunks** display with:
  - Chunk ID (unique identifier)
  - Title (document title)
  - Source (URL or file path)
  - Content preview (truncated if long)
  - **Detailed Metadata**:
    - Publish date (if available)
    - Effective date (if available)
    - Expiration date (if available)
    - Chunk type (conceptual, factual, procedural, etc.)
    - Confidence score (0-1 scale)
    - Retrieval rank (number)
- **Chunk expansion/collapse** functionality works
- **Visual indicators** for chunk quality and relevance

#### 1.4 Config Tab Content
**Steps:**
1. Open Details modal
2. Click on Config tab

**Expected Results:**
- Model information displays:
  - Model name (e.g., gpt-4o-mini)
  - Parameters: temperature, max_tokens, top_p
- System prompt displays with version information
- User instruction displays with role and version
- Retrieval configuration (if available):
  - top_k value
  - similarity_threshold
  - reranker_enabled flag

#### 1.5 Execution Tab Content
**Steps:**
1. Open Details modal
2. Click on Execution tab

**Expected Results:**
- Actual AI response displays in full
- Performance metrics show:
  - Total response time (in seconds)
  - Retrieval time (in seconds)
  - Generation time (in seconds)
  - Tokens used (number)
  - Chunks considered (number)
- Retrieval quality scores (if available):
  - Max similarity (0-1 scale)
  - Average similarity (0-1 scale)
  - Diversity score (0-1 scale)
- **User Feedback Section** (if available):
  - Rating display (1-5 stars or numeric scale)
  - Feedback category (e.g., accuracy, completeness, clarity)
  - User comment text
  - User concern text
  - Suggested improvement (if provided)
  - Feedback date with timestamp
  - Feedback source identifier
- **Visual Progress Bars** for quality metrics
- **Colored Tags** for feedback categories and status indicators

#### 1.6 Analysis Tab Content
**Steps:**
1. Open Details modal
2. Click on Analysis tab

**Expected Results:**
- Issue type and root cause analysis display
- Expected answer field populated with full text
- Acceptance criteria listed (may be numbered or bulleted)
- **Quality Scores with Visual Progress Bars**:
  - Context understanding (1-5 scale with colored progress bar)
  - Answer accuracy (1-5 scale with colored progress bar)
  - Answer completeness (1-5 scale with colored progress bar)
  - Clarity (1-5 scale with colored progress bar)
  - Citation quality (1-5 scale with colored progress bar)
- **Optimization suggestions** listed as bullet points or numbered list
- **Analysis notes** section with detailed observations
- **Analyst information**:
  - Analyzed by (name/email)
  - Analysis date (timestamp)
- **Visual Badges** for status indicators (if present)
- **Colored Tags** for issue categorization

#### 1.7 Modal Navigation
**Steps:**
1. Open Details modal
2. Test various navigation methods

**Expected Results:**
- Tab switching works smoothly without data loss
- Modal closes properly via:
  - Close button (X)
  - Clicking outside modal
  - Escape key
- Modal re-opens correctly after closing

## 2. Edit Button Testing

### Objective
Verify test case editing functionality works correctly with proper form validation, data persistence, and error handling.

### Test Scenarios

#### 2.1 Basic Edit Mode
**Steps:**
1. Navigate to Test Case Management page
2. Click the Edit button on any test case row
3. Observe the modal changes

**Expected Results:**
- Modal opens in edit mode (same as Details modal initially)
- Save and Cancel buttons appear in the footer
- Form fields become editable (text inputs, dropdowns, etc.)
- Edit mode indicator is visible

#### 2.2 Form Validation
**Steps:**
1. Open Edit mode for any test case
2. Try to save with empty required fields
3. Test various invalid inputs

**Expected Results:**
- Required field validation triggers (name, status, etc.)
- Error messages display clearly for invalid inputs
- Save button is disabled or shows appropriate error
- Form highlights problematic fields

#### 2.3 Field Editing - Basic Information
**Steps:**
1. Open Edit mode
2. Modify test case name and description
3. Change status, priority, domain, difficulty
4. Add/remove tags
5. Test all editable form fields

**Expected Results:**
- Text fields accept input correctly with proper validation
- Dropdowns show proper options (status: draft/approved/archived, priority: low/medium/high, etc.)
- Tags can be added (type + enter) and removed (click X) with color selection
- **Form validation messages** appear for invalid inputs
- **Character limits** are enforced for text fields
- **Required field indicators** (asterisks) show mandatory fields
- **Real-time validation** feedback as user types
- **Form state management** (dirty/pristine states) works correctly

#### 2.4 Field Editing - Analysis Section
**Steps:**
1. Open Edit mode
2. Navigate to Analysis tab
3. Modify issue type, root cause, expected answer
4. Adjust quality scores using sliders
5. Edit optimization suggestions
6. Test all analysis-related fields

**Expected Results:**
- **Text areas** accept multi-line input with proper formatting
- **Quality score sliders** work smoothly (1-5 scale) with real-time visual feedback
- **Issue type dropdown/select** shows available categories
- **Root cause analysis** text area supports detailed input
- **Expected answer** field supports long-form text
- **Acceptance criteria** text area supports structured input
- **Optimization suggestions** can be added/removed/edit as list items
- **Analysis notes** text area supports detailed observations
- **Form validation** ensures quality scores are within range
- **Auto-save functionality** (if implemented) works properly
- **Unsaved changes warning** appears when navigating away

#### 2.5 Save Functionality
**Steps:**
1. Make valid changes to multiple fields
2. Click Save button
3. Monitor Network tab in DevTools

**Expected Results:**
- PUT request sent to `/api/testcases/{id}`
- Request payload contains all modified data
- Success message appears (toast/notification)
- Modal closes after successful save
- Updated data reflects in the main table

#### 2.6 Cancel Functionality
**Steps:**
1. Make changes to various fields
2. Click Cancel button instead of Save

**Expected Results:**
- Confirmation dialog may appear (if changes were made)
- Modal closes without saving changes
- Original data remains unchanged in the table
- No API calls are made for cancel operation

#### 2.7 API Integration Testing
**Steps:**
1. Open Chrome DevTools Network tab
2. Make edits and save
3. Examine the API requests/responses

**Expected Results:**
- PUT request to `/api/testcases/{id}` with correct method
- Request headers include proper content-type
- Request body contains properly formatted JSON data
- Response includes success status and updated data
- Error responses are handled gracefully

## 3. Delete Button Testing

### Objective
Verify test case deletion functionality works safely with proper confirmation, error handling, and data consistency.

### Test Scenarios

#### 3.1 Delete Confirmation Dialog
**Steps:**
1. Navigate to Test Case Management page
2. Click the Delete button on any test case row

**Expected Results:**
- Confirmation dialog opens
- Dialog shows correct test case ID and name
- Warning message about permanent deletion
- Confirm and Cancel buttons are present
- Dialog can be closed via Cancel button or clicking outside

#### 3.2 Successful Deletion
**Steps:**
1. Click Delete button on a test case
2. Click Confirm in the confirmation dialog
3. Monitor Network tab

**Expected Results:**
- DELETE request sent to `/api/testcases/{id}`
- Success message appears after deletion
- Test case is removed from the table
- Table pagination updates correctly
- No orphaned data remains

#### 3.3 Delete Cancellation
**Steps:**
1. Click Delete button on a test case
2. Click Cancel in the confirmation dialog

**Expected Results:**
- Dialog closes without deletion
- Test case remains in the table
- No API calls are made
- Table state remains unchanged

#### 3.4 Error Handling
**Steps:**
1. Simulate network failure or server error
2. Attempt to delete a test case
3. Try deleting non-existent test case (if possible via API)

**Expected Results:**
- Error message displays appropriately
- Table state remains consistent
- User is informed of the failure reason
- Recovery options are provided

#### 3.5 Batch Operations (if applicable)
**Steps:**
1. Select multiple test cases (if selection is available)
2. Test bulk delete functionality

**Expected Results:**
- Multiple test cases can be selected
- Bulk delete confirmation shows selected count
- Progress indicators show deletion progress
- All selected items are removed successfully

## 4. Cross-Functional Testing

### Objective
Verify integration between different features and ensure data consistency across operations.

### Test Scenarios

#### 4.1 Data Consistency
**Steps:**
1. Edit a test case and save changes
2. Click Details to verify changes persisted
3. Refresh page and check data is still updated

**Expected Results:**
- Changes made in Edit mode reflect in Details view
- Data persists across page refreshes
- All views show consistent information

#### 4.2 Concurrent Operations Simulation
**Steps:**
1. Open Edit mode for a test case
2. In another tab, try to delete the same test case
3. Observe behavior

**Expected Results:**
- Proper conflict resolution occurs
- Appropriate error messages show
- Data integrity is maintained

#### 4.3 Error Recovery
**Steps:**
1. Perform operations during network issues
2. Test with invalid server responses
3. Verify loading states and error messages

**Expected Results:**
- Loading indicators show during API calls
- Error messages are clear and actionable
- Application recovers gracefully from errors

## 5. Accessibility Testing

### Objective
Verify the Test Case Management functionality is accessible to users with disabilities and follows WCAG guidelines.

### Test Scenarios

#### 5.1 Keyboard Navigation
**Steps:**
1. Navigate to Test Case Management page using only keyboard
2. Test Tab navigation through all interactive elements
3. Test Details, Edit, Delete buttons with keyboard
4. Test modal navigation and form submission with keyboard

**Expected Results:**
- Tab order follows logical sequence
- All buttons are reachable and activatable via keyboard
- Focus indicators are clearly visible
- Modal can be opened, navigated, and closed with keyboard
- Forms can be completed and submitted with keyboard
- Escape key closes modals
- Enter key activates buttons and submits forms

#### 5.2 Screen Reader Compatibility
**Steps:**
1. Enable screen reader (if available)
2. Navigate through test case table
3. Open and interact with modal dialogs
4. Complete form editing tasks

**Expected Results:**
- All interactive elements have appropriate ARIA labels
- Table headers are properly announced
- Modal dialogs are announced when opened
- Form fields have proper labels and descriptions
- Error messages are announced
- State changes (success/error) are communicated

#### 5.3 Visual Accessibility
**Steps:**
1. Test with high contrast mode
2. Test with larger text sizes
3. Test color blind accessibility
4. Test with reduced motion preferences

**Expected Results:**
- Sufficient color contrast ratios (4.5:1 minimum)
- Information not conveyed by color alone
- Text scales properly without breaking layout
- Animations respect reduced motion preferences
- Focus indicators remain visible at all times

## 6. Responsive Design Testing

### Objective
Verify the Test Case Management functionality works correctly across different screen sizes and devices.

### Test Scenarios

#### 6.1 Mobile Viewport Testing
**Steps:**
1. Resize browser to mobile width (375px - 768px)
2. Test table display and scrolling
3. Test modal display and interaction
4. Test form editing on small screens

**Expected Results:**
- Table adapts with horizontal scrolling or responsive design
- Modals fit within viewport and are scrollable if needed
- Forms remain usable on small screens
- Buttons remain large enough for touch interaction
- Text remains readable without horizontal scrolling

#### 6.2 Tablet Viewport Testing
**Steps:**
1. Resize browser to tablet width (768px - 1024px)
2. Test layout and functionality
3. Test modal and form interactions

**Expected Results:**
- Layout adapts appropriately to tablet screen size
- All functionality remains accessible
- Touch targets remain appropriately sized
- Performance remains acceptable

## 7. Cross-Browser Compatibility Testing

### Objective
Verify functionality works correctly across different web browsers.

### Test Scenarios

#### 7.1 Browser Matrix Testing
**Steps:**
1. Test functionality in Chrome (primary browser)
2. Test in Firefox
3. Test in Safari (if available)
4. Test in Edge (if available)

**Expected Results:**
- All features work consistently across browsers
- No browser-specific JavaScript errors
- CSS renders correctly across browsers
- Performance is acceptable across browsers

#### 7.2 API Compatibility
**Steps:**
1. Monitor API requests in different browsers
2. Test error handling across browsers
3. Verify data consistency across browsers

**Expected Results:**
- API calls work consistently across browsers
- Error handling is consistent
- Data formatting remains consistent

## 8. Edge Cases and Boundary Testing

### Objective
Test boundary conditions and unusual scenarios to ensure robustness.

### Test Scenarios

#### 8.1 Empty States
**Steps:**
1. Test with no test cases in the system
2. Test Details/Edit/Delete on empty table
3. Test modal behavior with missing data sections

**Expected Results:**
- Appropriate empty state messages display
- Buttons are disabled when no data exists
- User guidance is provided
- Missing sections show proper fallback messages

#### 8.2 Data Validation Limits
**Steps:**
1. Test with extremely long text inputs (1000+ characters)
2. Test with special characters and emojis
3. Test with boundary values for numeric fields
4. Test with null/undefined values in form fields
5. Test with malformed data in API responses

**Expected Results:**
- Input validation handles edge cases gracefully
- Data sanitization prevents security issues
- System remains stable with unexpected inputs
- Error messages are user-friendly and specific

#### 8.3 Performance Testing
**Steps:**
1. Test with large datasets (100+ test cases)
2. Measure modal opening times
3. Test response times for save/delete operations
4. Monitor memory usage during extended sessions
5. Test with large content in text areas

**Expected Results:**
- Performance remains acceptable (<2 seconds for most operations)
- Loading indicators show for operations >1 second
- Memory usage remains reasonable
- Large content doesn't break UI or performance

#### 8.4 Missing Data Fields
**Steps:**
1. Test with test cases missing optional fields
2. Test behavior when API returns incomplete data
3. Test with corrupted or inconsistent data
4. Test missing user feedback or analysis sections

**Expected Results:**
- System gracefully handles missing optional fields
- Appropriate fallbacks or placeholders show
- No crashes or console errors
- User gets clear indication of missing data

#### 8.5 State Management Testing
**Steps:**
1. Test rapid clicking of buttons (double-click prevention)
2. Test switching between Details/Edit modes rapidly
3. Test concurrent operations on multiple test cases
4. Test browser back/forward navigation during modal interactions

**Expected Results:**
- Button debouncing prevents duplicate operations
- State transitions are smooth and consistent
- Concurrent operations are properly queued or rejected
- Browser navigation doesn't cause data loss or corruption

## Chrome DevTools Testing Guidelines

### Network Monitoring
1. Keep Network tab open throughout testing
2. Monitor API calls for each operation
3. Verify request/response formats
4. Check for unnecessary duplicate calls
5. Verify error responses are handled properly

### Console Monitoring
1. Keep Console tab open for JavaScript errors
2. Watch for warnings or deprecated API usage
3. Verify no memory leaks during extended testing

### Element Inspection
1. Use Elements tab to verify DOM structure
2. Check CSS classes and styling
3. Verify accessibility attributes
4. Test responsive behavior

## Test Execution Checklist

### Before Starting
- [ ] Backend and frontend servers are running
- [ ] Chrome DevTools are open and configured
- [ ] Test data is available in the system
- [ ] Network tab is clear and ready for monitoring

### During Testing
- [ ] Each test scenario is executed systematically
- [ ] Screenshots are taken for important states
- [ ] Network requests are verified for each operation
- [ ] Errors and unexpected behaviors are documented

### After Testing
- [ ] All test scenarios are completed
- [ ] Results are documented with pass/fail status
- [ ] Issues are prioritized and reported
- [ ] Test coverage is reviewed and gaps identified

## Session Continuity Instructions

For new sessions picking up this testing plan:

1. **Environment Setup**: Ensure both backend (localhost:8000) and frontend (localhost:3000) are running
2. **Navigation**: Go to the Test Case Management page via the main navigation menu
3. **Prerequisites**: Verify test cases are loaded in the table before proceeding
4. **DevTools**: Open Chrome DevTools (F12) and keep Network tab visible throughout testing
5. **Documentation**: Record results, issues, and observations for each test scenario

## Current Implementation Status

- ✅ System prompt and user instruction functionality implemented for all test cases
- ✅ Test case data structure includes all required fields
- ✅ Modal components implemented with 5 tabs
- ✅ Edit functionality with form validation
- ✅ Delete functionality with confirmation
- ✅ API integration established
- ⏳ Comprehensive testing required (this plan)

## Next Steps After Testing

1. Document any bugs or issues found
2. Prioritize fixes based on severity
3. Implement improvements based on testing results
4. Consider additional features based on user feedback
5. Update documentation with any discovered requirements