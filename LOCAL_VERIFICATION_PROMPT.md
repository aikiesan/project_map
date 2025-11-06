# Local Verification Prompt for Claude Code Desktop

Copy and paste this entire prompt into your local Claude Code desktop session to perform the final verification of the Enhanced Scientific References System.

---

## PROMPT START

I need your help to verify and test the Enhanced Scientific References System that was implemented on branch `claude/scientific-references-011CUqck8tRQ7YCqmKkEgarS` before merging to main.

### Context

The Enhanced Scientific References System adds a new "Base Panorama" tab to the References page with 58 scientific papers from the Panorama CP2B database. The implementation includes:

**Features Added**:
- New tab with 58 scientific papers from Panorama CP2B
- Full-text search across papers
- Category filtering (Agricultural, Livestock, Urban, Industrial, etc.)
- Year range filtering
- Dual citation formats (ABNT and APA)
- Export capabilities (BibTeX, CSV, Text)
- Live statistics dashboard
- Professional paper cards with validation badges

**Files Created** (5 new files):
1. `data/panorama_scientific_papers.json` - 58 papers data
2. `src/data/references/enhanced_references_loader.py` - Data model and loader
3. `src/ui/components/enhanced_references_ui.py` - UI components
4. `REFERENCES_ENHANCEMENT_GUIDE.md` - User guide
5. `IMPLEMENTATION_SUMMARY.md` - Technical documentation

**Files Modified** (1 file):
- `src/ui/pages/references_v1.py` - Enhanced with new tab

**Commits** (5 total):
- `dc5eb3a` - Verification report
- `1225ba5` - Implementation summary
- `121775a` - User guide
- `bafb675` - Part 2: Integration
- `6e94650` - Part 1: Infrastructure

### Your Tasks

Please help me with the following verification tasks:

#### 1. Fetch and Checkout the Branch

First, fetch the branch and checkout locally:

```bash
git fetch origin claude/scientific-references-011CUqck8tRQ7YCqmKkEgarS
git checkout claude/scientific-references-011CUqck8tRQ7YCqmKkEgarS
```

Verify you're on the correct branch and show me the recent commits.

#### 2. Review File Changes

Show me:
- List of all files changed between base commit `f3e39b5` and current HEAD
- Statistics of changes (lines added/removed)
- Brief summary of what changed in `src/ui/pages/references_v1.py`

#### 3. Validate JSON Data

Check the `data/panorama_scientific_papers.json` file:
- Is it valid JSON?
- How many papers does it contain?
- Show me a sample of 2-3 papers with their structure
- Check for any data quality issues (empty fields, null values, etc.)
- What's the year range of papers?

#### 4. Code Review

Review the Python files and check:
- **Syntax**: Do all Python files compile without errors?
- **Imports**: Are all imports valid and available in the project?
- **Integration**: Review `src/ui/pages/references_v1.py` - does it properly integrate the new components?
- **SOLID Principles**: Does the code follow good practices?

Specifically review:
- `src/data/references/enhanced_references_loader.py` (lines 1-100)
- `src/ui/components/enhanced_references_ui.py` (lines 1-100)
- `src/ui/pages/references_v1.py` (lines 25-80)

#### 5. Breaking Changes Analysis

Check if there are any breaking changes:
- Compare the old and new `_render_stats_banner()` function signature
- Are all existing tabs (Agricultural, Livestock, Co-digestion, Data Sources, Methodologies) still present?
- Is any existing functionality removed or modified in a breaking way?

#### 6. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Once running, help me test:

**Basic Functionality** (5 minutes):
- Navigate to "📚 Referências Científicas" page
- Verify header shows statistics (should show: 58 papers, 6 categories, etc.)
- Check all 6 tabs are visible
- Click on "📚 Base Panorama" tab
- Verify papers display as cards
- Check if statistics banner shows dynamic numbers

**Search & Filter** (5 minutes):
- Search for "cana" - how many results?
- Search for "anaerobic" - how many results?
- Search for "xyz123nonexistent" - should show "no results"
- Filter by "Agricultural" category - verify results
- Adjust year range slider - verify filtering works
- Switch between ABNT and APA citation formats - verify citations update

**Export Functionality** (3 minutes):
- Click "Exportar como BibTeX" - does it download?
- Click "Exportar como CSV" - does it download?
- Try copying formatted text - does it work?
- Verify exported files have content

**Regression Testing** (2 minutes):
- Click through all original 5 tabs (Agricultural, Livestock, Co-digestion, Data Sources, Methodologies)
- Verify they still work as before
- Check browser console for any errors (press F12)
- Check terminal for any Python errors

#### 7. Performance Check

While the app is running:
- How long does the References page take to load initially?
- How fast is the search (type "cana" and see response time)?
- Are there any lag or freezing issues?
- Check Streamlit cache status (look for any cache warnings)

#### 8. Documentation Review

Quickly review these documentation files and tell me if they're comprehensive:
- `REFERENCES_ENHANCEMENT_GUIDE.md`
- `IMPLEMENTATION_SUMMARY.md`
- `PRE_MERGE_VERIFICATION_REPORT.md`

#### 9. Final Assessment

Based on all your checks, provide:

**Summary Report**:
- Are all files present and valid? ✅/❌
- Is the JSON data structure correct? ✅/❌
- Do all Python files compile? ✅/❌
- Are there any breaking changes? YES/NO
- Did the application start successfully? ✅/❌
- Do all features work as described? ✅/❌
- Is performance acceptable? ✅/❌
- Any errors or issues found? List them

**Recommendation**:
- Overall Status: READY TO MERGE / NEEDS FIXES / NEEDS REVIEW
- Risk Level: LOW / MEDIUM / HIGH
- Your confidence level in merging: 1-10

**Issues Found** (if any):
List any issues, bugs, or concerns you discovered during testing.

#### 10. Merge Decision

If everything looks good and you recommend merging, show me the exact commands to:
1. Merge the branch to main
2. Push to origin
3. Clean up the feature branch (optional)

If there are issues, suggest what needs to be fixed before merging.

---

### Expected Outcomes

Based on the pre-verification report, these are the expected outcomes:

**File Verification**:
- ✅ 5 new files created (total ~91KB)
- ✅ 1 file modified (+94, -18 lines)
- ✅ All files have correct permissions

**Data Validation**:
- ✅ JSON is valid with 58 papers
- ⚠️ Note: 55/58 papers have empty journal field (database under development)
- ⚠️ Note: Only 4/58 papers marked as validated (expected)

**Code Quality**:
- ✅ All Python files compile without errors
- ✅ SOLID principles followed
- ✅ No breaking changes

**Application Testing**:
- ✅ App should start without errors
- ✅ All 6 tabs should be visible and functional
- ✅ Search should return relevant results
- ✅ Filters should work correctly
- ✅ Export should download files
- ✅ No console errors expected

**Performance**:
- ✅ Page load < 3 seconds
- ✅ Search response < 1 second
- ✅ No lag or freezing

**Recommendation from Pre-Verification**:
- Status: ✅ READY FOR MERGE
- Risk Level: 🟢 LOW
- Grade: A- (90/100)

---

### Additional Notes

**Data Quality Context**:
The Panorama CP2B database is still under development, so some papers have incomplete metadata:
- 55/58 papers have empty journal field
- Only 4/58 papers are fully validated
- This is expected and the code handles it gracefully

**No Breaking Changes**:
All existing functionality is preserved. The only changes to existing code are:
- Stats banner now shows dynamic data instead of hardcoded "50+"
- Added 6th tab (new feature)
- All original 5 tabs unchanged

**Rollback Available**:
If any issues are found post-merge, easy rollback:
```bash
git revert -m 1 <merge-commit-hash>
# or
git reset --hard f3e39b5
```

---

### Questions to Answer

Please answer these specific questions during your verification:

1. Does `data/panorama_scientific_papers.json` exist and is it valid JSON?
2. How many papers are in the JSON file?
3. Do all 3 Python files compile without syntax errors?
4. Does the app start successfully with `streamlit run app.py`?
5. Can you see all 6 tabs on the References page?
6. Does the "Base Panorama" tab load and show papers?
7. Does search work when you type "cana"?
8. Can you switch between ABNT and APA citation formats?
9. Does BibTeX export download a file?
10. Are there any errors in browser console or terminal?
11. Do the original 5 tabs still work as before?
12. What's the page load time for the References page?
13. Based on your testing, is this ready to merge?
14. What's your confidence level (1-10) in merging this?
15. Any issues or concerns?

---

### Success Criteria

This branch is ready to merge if:
- ✅ All files are present and valid
- ✅ JSON data loads successfully
- ✅ All Python files compile
- ✅ App starts without errors
- ✅ All 6 tabs are functional
- ✅ Search and filters work
- ✅ Export functionality works
- ✅ No console or terminal errors
- ✅ Original tabs still work (no regression)
- ✅ Performance is acceptable (< 3s load)
- ✅ No breaking changes detected

---

### Final Request

After completing all verification tasks, provide me with:

1. **Executive Summary** (3-5 sentences):
   - What was tested
   - What the results were
   - Your recommendation

2. **Detailed Findings**:
   - List of all checks performed
   - Results for each check (PASS/FAIL)
   - Any issues found

3. **Merge Recommendation**:
   - Status: APPROVE / NEEDS FIXES / NEEDS REVIEW
   - Risk Assessment: LOW / MEDIUM / HIGH
   - Confidence: X/10

4. **Merge Commands** (if approved):
   - Exact git commands to merge safely

Thank you for your thorough verification!

## PROMPT END

---

## How to Use This Prompt

1. **Open Claude Code Desktop** on your local machine
2. **Navigate** to your CP2B Maps project directory
3. **Copy** everything between "PROMPT START" and "PROMPT END" above
4. **Paste** into Claude Code chat
5. **Wait** for Claude to complete all verification tasks
6. **Review** the results and make merge decision

**Estimated Time**: 15-20 minutes for complete verification

---

## What Claude Will Do

Claude will systematically:
1. ✅ Fetch and checkout the branch
2. ✅ Review all file changes
3. ✅ Validate JSON data structure
4. ✅ Check Python syntax and imports
5. ✅ Analyze for breaking changes
6. ✅ Start and test the application
7. ✅ Test all features (search, filter, export)
8. ✅ Check for regression issues
9. ✅ Measure performance
10. ✅ Review documentation
11. ✅ Provide comprehensive report
12. ✅ Give merge recommendation

---

## After Verification

Based on Claude's findings:

**If APPROVED**:
```bash
# Claude will provide exact commands, typically:
git checkout main
git merge --no-ff claude/scientific-references-011CUqck8tRQ7YCqmKkEgarS
git push origin main
```

**If ISSUES FOUND**:
- Claude will list specific issues
- Suggest fixes needed
- You can address issues before merging

**If UNCERTAIN**:
- Review the detailed findings
- Ask Claude for clarification
- Run additional tests

---

## Support

If you encounter any issues during verification:
1. Check that all dependencies are installed (`pip install -r requirements.txt`)
2. Ensure you're in the correct directory
3. Verify git repository is clean (`git status`)
4. Check that Streamlit is installed (`streamlit --version`)

---

**Ready to verify? Copy the prompt above and paste it into your local Claude Code!** 🚀
