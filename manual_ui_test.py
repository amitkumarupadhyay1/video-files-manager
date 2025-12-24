"""
Manual UI Testing Checklist for Video Management System
Run this alongside the application to verify all UI components
"""

print("="*70)
print("VIDEO MANAGEMENT SYSTEM - MANUAL UI TESTING CHECKLIST")
print("="*70)
print("\nInstructions: Launch the application and go through each test.")
print("Mark each test as PASS or FAIL\n")

tests = {
    "1. Application Launch": [
        "[ ] Application window opens without errors",
        "[ ] Main window displays with correct title",
        "[ ] Toolbar is visible with all buttons",
        "[ ] Status bar shows statistics at bottom",
        "[ ] Video list area is visible",
        "[ ] Details panel is visible on the right"
    ],
    
    "2. Activity Management": [
        "[ ] Click '📁 Manage Activities' button",
        "[ ] Activity Manager dialog opens",
        "[ ] Click 'Add Activity' button",
        "[ ] Enter activity name, description, class, section",
        "[ ] Activity is added to the list",
        "[ ] Select an activity and click 'Edit'",
        "[ ] Edit dialog opens with pre-filled data",
        "[ ] Make changes and save",
        "[ ] Changes are reflected in the list",
        "[ ] Select an activity and click 'Delete'",
        "[ ] Confirmation dialog appears",
        "[ ] Activity is deleted successfully"
    ],
    
    "3. Class/Section Management": [
        "[ ] Click '🏫 Manage Classes' button",
        "[ ] Class Manager dialog opens",
        "[ ] Add a new class",
        "[ ] Edit existing class",
        "[ ] Delete a class",
        "[ ] Click '📚 Manage Sections' button",
        "[ ] Section Manager dialog opens",
        "[ ] Add a new section",
        "[ ] Edit existing section",
        "[ ] Delete a section"
    ],
    
    "4. Add Video": [
        "[ ] Click '➕ Add Video' button",
        "[ ] Add Video dialog opens",
        "[ ] Activity dropdown is populated",
        "[ ] Click '+' button to add new activity from dialog",
        "[ ] Enter video title",
        "[ ] Enter description",
        "[ ] Enter tags (comma-separated)",
        "[ ] Click '📁 Browse...' to select video file",
        "[ ] File dialog opens",
        "[ ] Select a video file",
        "[ ] File path is displayed",
        "[ ] Enter YouTube URL",
        "[ ] Select class from dropdown",
        "[ ] Select section from dropdown",
        "[ ] Set event date",
        "[ ] Check 'Auto-increment version' checkbox",
        "[ ] Click '💾 Save Video'",
        "[ ] Video is added to the list",
        "[ ] Thumbnail is generated"
    ],
    
    "5. Edit Video": [
        "[ ] Select a video from the list",
        "[ ] Click '✏️ Edit Video' button",
        "[ ] Edit Video dialog opens",
        "[ ] All fields are pre-filled with current data",
        "[ ] Modify title",
        "[ ] Modify description",
        "[ ] Modify tags",
        "[ ] Change activity",
        "[ ] Click '💾 Save Changes'",
        "[ ] Changes are reflected in the video list"
    ],
    
    "6. Video Details Panel": [
        "[ ] Click on a video in the list",
        "[ ] Details panel on right shows video information",
        "[ ] Thumbnail is displayed",
        "[ ] Title is shown",
        "[ ] Description is shown",
        "[ ] Tags are displayed",
        "[ ] Activity name is shown",
        "[ ] Class and section are shown",
        "[ ] File size and duration are shown",
        "[ ] Event date is shown",
        "[ ] Version number is shown"
    ],
    
    "7. Video Playback - Local": [
        "[ ] Select a video with local copy",
        "[ ] Click '🎬 Play Local Copy' button",
        "[ ] Video player window opens",
        "[ ] Thumbnail preview is shown",
        "[ ] Click play button",
        "[ ] Video starts playing",
        "[ ] Click pause button",
        "[ ] Video pauses",
        "[ ] Use seek slider to jump to different position",
        "[ ] Adjust volume slider",
        "[ ] Volume changes accordingly",
        "[ ] Click stop button",
        "[ ] Video stops and returns to beginning",
        "[ ] Close player window"
    ],
    
    "8. Video Playback - YouTube": [
        "[ ] Select a video with YouTube link",
        "[ ] Click '▶️ Play YouTube Link' button",
        "[ ] YouTube player window opens",
        "[ ] Video loads in embedded player",
        "[ ] Video plays correctly",
        "[ ] Close player window"
    ],
    
    "9. Search Functionality": [
        "[ ] Type text in search box",
        "[ ] Video list filters in real-time",
        "[ ] Search results are accurate",
        "[ ] Clear search box",
        "[ ] All videos are shown again",
        "[ ] Click '🔍 Advanced Search' button",
        "[ ] Advanced Search dialog opens",
        "[ ] Enter search term",
        "[ ] Select class filter",
        "[ ] Select section filter",
        "[ ] Select format filter",
        "[ ] Set date range",
        "[ ] Click 'Search'",
        "[ ] Results match all criteria"
    ],
    
    "10. Tag Management": [
        "[ ] Click '🏷️ Manage Tags' button",
        "[ ] Tag Manager opens",
        "[ ] Click 'Create Tag'",
        "[ ] Enter tag name",
        "[ ] Choose tag color",
        "[ ] Enter description",
        "[ ] Tag is created",
        "[ ] Tags are listed",
        "[ ] Edit a tag",
        "[ ] Delete a tag",
        "[ ] Filter videos by tag"
    ],
    
    "11. Collection Management": [
        "[ ] Click '📚 Manage Collections' button",
        "[ ] Collection Manager opens",
        "[ ] Click 'Create Collection'",
        "[ ] Enter collection name",
        "[ ] Enter description",
        "[ ] Choose color",
        "[ ] Collection is created",
        "[ ] Right-click on a video",
        "[ ] Select 'Add to Collection'",
        "[ ] Choose collection",
        "[ ] Video is added to collection",
        "[ ] View collection videos",
        "[ ] Remove video from collection",
        "[ ] Delete collection"
    ],
    
    "12. Context Menu": [
        "[ ] Right-click on a video",
        "[ ] Context menu appears",
        "[ ] 'Play Local Copy' option is visible",
        "[ ] 'Play YouTube Link' option is visible",
        "[ ] 'Open File Location' option is visible",
        "[ ] 'Edit' option is visible",
        "[ ] 'Delete' option is visible",
        "[ ] 'Add to Collection' option is visible",
        "[ ] Click 'Open File Location'",
        "[ ] File explorer opens to video location"
    ],
    
    "13. Version Timeline": [
        "[ ] Select a video with multiple versions",
        "[ ] Click 'Version Timeline' button",
        "[ ] Version Timeline dialog opens",
        "[ ] All versions are listed",
        "[ ] Version numbers are correct",
        "[ ] Dates are shown",
        "[ ] Can view details of each version"
    ],
    
    "14. Export Functionality": [
        "[ ] Click '📊 Export Activities' button",
        "[ ] Export dialog opens",
        "[ ] Select activities to export",
        "[ ] Choose export format (Excel/PDF)",
        "[ ] Click 'Export'",
        "[ ] File save dialog appears",
        "[ ] Choose location and save",
        "[ ] Export completes successfully",
        "[ ] Open exported file",
        "[ ] Data is correctly formatted"
    ],
    
    "15. Delete Video": [
        "[ ] Select a video",
        "[ ] Click '🗑️ Delete Video' button",
        "[ ] Confirmation dialog appears",
        "[ ] Click 'Yes' to confirm",
        "[ ] Video is removed from list",
        "[ ] Status bar updates video count"
    ],
    
    "16. Statistics Display": [
        "[ ] Check status bar at bottom",
        "[ ] Total videos count is displayed",
        "[ ] Total activities count is displayed",
        "[ ] Total collections count is displayed",
        "[ ] Total tags count is displayed",
        "[ ] Storage used is displayed",
        "[ ] Counts update when adding/deleting items"
    ],
    
    "17. Refresh Functionality": [
        "[ ] Click '🔄 Refresh' button",
        "[ ] Video list refreshes",
        "[ ] Statistics update",
        "[ ] No errors occur"
    ],
    
    "18. Window Resizing": [
        "[ ] Resize main window",
        "[ ] All components resize properly",
        "[ ] No overlapping elements",
        "[ ] Scroll bars appear when needed",
        "[ ] Layout remains usable"
    ],
    
    "19. Error Handling": [
        "[ ] Try to add video without title",
        "[ ] Error message appears",
        "[ ] Try to add video without activity",
        "[ ] Error message appears",
        "[ ] Try to delete activity with videos",
        "[ ] Appropriate warning/confirmation appears",
        "[ ] Try to play non-existent local file",
        "[ ] Error message is user-friendly"
    ],
    
    "20. Performance": [
        "[ ] Application launches quickly (<5 seconds)",
        "[ ] Search results appear instantly",
        "[ ] Video list scrolls smoothly",
        "[ ] No lag when switching between videos",
        "[ ] Dialogs open quickly",
        "[ ] No freezing or hanging"
    ]
}

print("\n" + "="*70)
for category, checklist in tests.items():
    print(f"\n{category}")
    print("-" * 70)
    for item in checklist:
        print(f"  {item}")

print("\n" + "="*70)
print("TESTING TIPS:")
print("="*70)
print("1. Test with different video formats (MP4, AVI, MOV, etc.)")
print("2. Test with videos of different sizes")
print("3. Test with long video titles and descriptions")
print("4. Test with special characters in names")
print("5. Test with many videos (50+) to check performance")
print("6. Test all keyboard shortcuts")
print("7. Test all buttons and menu items")
print("8. Check for any console errors or warnings")
print("9. Verify data persistence (close and reopen app)")
print("10. Test on different screen resolutions if possible")
print("="*70)
