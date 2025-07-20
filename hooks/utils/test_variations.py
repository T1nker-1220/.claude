#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import random

def get_simple_notification(context: str, tool: str) -> str:
    """Generate varied voice notifications for each tool with random selection."""
    if context == "permission_request":
        # Multiple permission request variations
        permission_variations = {
            "Read": ["Permission for Read", "Claude wants to read a file", "Requesting read access", "Need permission to read"],
            "Write": ["Permission for Write", "Claude wants to write a file", "Requesting write access", "Need permission to write"],
            "Edit": ["Permission for Edit", "Claude wants to edit a file", "Requesting edit access", "Need permission to edit"],
            "MultiEdit": ["Permission for MultiEdit", "Claude wants to edit multiple files", "Requesting multi-edit access", "Need permission for batch editing"],
            "Bash": ["Permission for Bash", "Claude wants to run a command", "Requesting terminal access", "Need permission for command"],
            "LS": ["Permission for LS", "Claude wants to list files", "Requesting directory access", "Need permission to browse"],
            "Grep": ["Permission for Grep", "Claude wants to search files", "Requesting search access", "Need permission to search"],
            "Glob": ["Permission for Glob", "Claude wants to find files", "Requesting file search", "Need permission to locate files"],
            "Update": ["Permission for Update", "Claude wants to update", "Requesting update access", "Need permission to update"],
            "Task": ["Permission for Task", "Claude wants to delegate", "Requesting task access", "Need permission for sub-task"],
            "Plan": ["Permission for Plan", "Claude wants to plan", "Requesting planning access", "Need permission to plan"]
        }
        variations = permission_variations.get(tool, [f"Permission for {tool}", f"Claude needs {tool} access"])
        return random.choice(variations)
    
    elif context == "tool_completion":
        # Multiple completion message variations
        completion_variations = {
            "Read": ["Read complete", "File loaded", "Reading finished", "Got the file content"],
            "Write": ["Write complete", "File saved", "Writing finished", "File created successfully"],
            "Edit": ["Edit complete", "File updated", "Changes saved", "Editing finished"],
            "MultiEdit": ["MultiEdit complete", "Multiple files updated", "Batch editing done", "All changes saved"],
            "Bash": ["Command complete", "Terminal finished", "Command executed", "Shell operation done"],
            "LS": ["Directory listed", "Files enumerated", "Listing complete", "Directory scanned"],
            "Grep": ["Search complete", "Matches found", "Search finished", "Pattern search done"],
            "Glob": ["Files found", "Pattern matched", "File search complete", "Globbing finished"],
            "Update": ["Update complete", "Successfully updated", "Update finished", "Changes applied"],
            "Task": ["Task complete", "Sub-task finished", "Delegation done", "Task executed"]
        }
        variations = completion_variations.get(tool, [f"{tool} complete", f"{tool} finished", f"{tool} done"])
        return random.choice(variations)
    
    elif context == "session_end":
        session_variations = []
        if tool and any(keyword in tool.lower() for keyword in ["commit", "git", "file"]):
            session_variations = [
                "Session complete with changes",
                "Work finished, changes saved", 
                "Claude done, files updated",
                "Session ended, work committed"
            ]
        else:
            session_variations = [
                "Claude session complete",
                "Work finished successfully",
                "Claude session ended",
                "All done, session closed"
            ]
        return random.choice(session_variations)
    
    elif context == "error_notification":
        error_variations = [
            "Error occurred",
            "Something went wrong",
            "Claude encountered an issue",
            "Operation failed"
        ]
        return random.choice(error_variations)
    
    elif context == "waiting":
        waiting_variations = [
            "Claude ready",
            "Ready for input",
            "Claude standing by",
            "Waiting for instructions"
        ]
        return random.choice(waiting_variations)
    
    elif context == "compact_notification":
        if "automatic" in tool.lower():
            auto_variations = [
                "Automatically compacting conversation",
                "Auto-compacting the chat",
                "Conversation being compressed",
                "Auto-tidying the session"
            ]
            return random.choice(auto_variations)
        elif "manual" in tool.lower():
            manual_variations = [
                "Manually compacting conversation", 
                "Compacting on request",
                "User-triggered compression",
                "Manual conversation cleanup"
            ]
            return random.choice(manual_variations)
        else:
            general_variations = [
                "Compacting the conversation",
                "Tidying up the chat",
                "Conversation cleanup",
                "Compressing the session"
            ]
            return random.choice(general_variations)
    
    else:
        general_variations = [
            "Claude notification",
            "Claude update",
            "System message",
            "Claude alert"
        ]
        return random.choice(general_variations)

def test_random_variations():
    """Test that random variations are working properly."""
    
    print("Testing Random Text Variations")
    print("=" * 40)
    
    # Test different contexts and tools
    test_cases = [
        ("permission_request", "Read"),
        ("permission_request", "Write"), 
        ("permission_request", "Bash"),
        ("tool_completion", "Read"),
        ("tool_completion", "Write"),
        ("tool_completion", "Edit"),
        ("tool_completion", "Bash"),
        ("session_end", "saved files"),
        ("session_end", "general"),
        ("waiting", ""),
        ("error_notification", ""),
        ("compact_notification", "automatic"),
        ("compact_notification", "manual")
    ]
    
    # Generate multiple variations for each test case
    for context, tool in test_cases:
        print(f"\n{context} - {tool}:")
        variations = set()
        
        # Generate 10 samples to see variety
        for i in range(10):
            text = get_simple_notification(context, tool)
            variations.add(text)
        
        # Show all unique variations found
        for i, variation in enumerate(sorted(variations), 1):
            print(f"  {i}. {variation}")
        
        print(f"  -> Found {len(variations)} unique variations")

if __name__ == "__main__":
    test_random_variations()