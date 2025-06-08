# update_channels.py
import os
import re
from datetime import datetime

def update_channels_cookie():
    # Get new cookie from GitHub secrets
    new_cookie = os.environ.get('NEW_COOKIE')
    
    if not new_cookie:
        print("❌ NEW_COOKIE not found in secrets")
        return False
    
    # Check if channels.m3u exists
    if not os.path.exists('channels.m3u'):
        print("❌ channels.m3u file not found!")
        return False
    
    print(f"🔄 Updating cookie in channels.m3u...")
    
    try:
        # Read the current file
        with open('channels.m3u', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Pattern 1: Replace Cookie: header (common in HTTP headers)
        if re.search(r'Cookie:\s*[^\r\n]+', content, re.IGNORECASE):
            content = re.sub(
                r'Cookie:\s*[^\r\n]+',
                f'Cookie: {new_cookie}',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated Cookie: header format")
        
        # Pattern 2: Replace #EXTVLCOPT:http-cookie= (VLC format)
        if re.search(r'#EXTVLCOPT:http-cookie=[^\r\n]*', content, re.IGNORECASE):
            content = re.sub(
                r'#EXTVLCOPT:http-cookie=[^\r\n]*',
                f'#EXTVLCOPT:http-cookie={new_cookie}',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated #EXTVLCOPT:http-cookie format")
        
        # Pattern 3: Replace cookie= parameter in URLs
        if re.search(r'cookie=[^&\s\r\n]+', content, re.IGNORECASE):
            content = re.sub(
                r'cookie=[^&\s\r\n]+',
                f'cookie={new_cookie}',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated cookie= parameter in URLs")
        
        # Pattern 4: Replace #EXT-X-SESSION-DATA with cookie (HLS format)
        if re.search(r'#EXT-X-SESSION-DATA:DATA-ID="COOKIE"', content, re.IGNORECASE):
            content = re.sub(
                r'#EXT-X-SESSION-DATA:DATA-ID="COOKIE",VALUE="[^"]*"',
                f'#EXT-X-SESSION-DATA:DATA-ID="COOKIE",VALUE="{new_cookie}"',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated #EXT-X-SESSION-DATA cookie format")
        
        # Pattern 5: Custom pattern - you can add your specific format here
        # Example for different formats:
        
        # If your cookie is in |Cookie=format
        if re.search(r'\|Cookie=[^\|\r\n]*', content, re.IGNORECASE):
            content = re.sub(
                r'\|Cookie=[^\|\r\n]*',
                f'|Cookie={new_cookie}',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated |Cookie= format")
        
        # If your cookie is in &cookie= format
        if re.search(r'&cookie=[^&\s\r\n]*', content, re.IGNORECASE):
            content = re.sub(
                r'&cookie=[^&\s\r\n]*',
                f'&cookie={new_cookie}',
                content,
                flags=re.IGNORECASE
            )
            changes_made += 1
            print("✅ Updated &cookie= format")
        
        # Check if any changes were made
        if content != original_content:
            # Write the updated content back
            with open('channels.m3u', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create status file
            with open('update_status.txt', 'w') as f:
                f.write(f"last_updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                f.write(f"status: success\n")
                f.write(f"changes_made: {changes_made}\n")
                f.write(f"patterns_updated: {changes_made}\n")
            
            print(f"✅ Successfully updated channels.m3u!")
            print(f"📊 Total patterns updated: {changes_made}")
            return True
        else:
            print("ℹ️  No cookie patterns found to update in channels.m3u")
            
            # Create status file for no changes
            with open('update_status.txt', 'w') as f:
                f.write(f"last_updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                f.write(f"status: no_changes\n")
                f.write(f"reason: No cookie patterns found\n")
            
            return False
            
    except Exception as e:
        print(f"❌ Error updating channels.m3u: {e}")
        
        # Create error status file
        with open('update_status.txt', 'w') as f:
            f.write(f"last_updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"status: error\n")
            f.write(f"error: {str(e)}\n")
        
        return False

def show_current_cookie_patterns():
    """Helper function to show what cookie patterns exist in the file"""
    if not os.path.exists('channels.m3u'):
        return
    
    try:
        with open('channels.m3u', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Current cookie patterns found:")
        
        # Check various patterns
        patterns = [
            (r'Cookie:\s*[^\r\n]+', 'Cookie: header'),
            (r'#EXTVLCOPT:http-cookie=[^\r\n]*', '#EXTVLCOPT:http-cookie'),
            (r'cookie=[^&\s\r\n]+', 'cookie= parameter'),
            (r'#EXT-X-SESSION-DATA:DATA-ID="COOKIE"[^\r\n]*', 'HLS SESSION-DATA'),
            (r'\|Cookie=[^\|\r\n]*', '|Cookie= format'),
            (r'&cookie=[^&\s\r\n]*', '&cookie= format'),
        ]
        
        found_any = False
        for pattern, description in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_any = True
                print(f"   - {description}: {len(matches)} occurrence(s)")
                # Show first match as example (truncated for security)
                example = matches[0][:50] + "..." if len(matches[0]) > 50 else matches[0]
                print(f"     Example: {example}")
        
        if not found_any:
            print("   - No recognizable cookie patterns found")
            
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    print("🍪 Starting channels.m3u cookie update...")
    
    # Show current patterns (for debugging)
    show_current_cookie_patterns()
    
    # Update the cookie
    success = update_channels_cookie()
    
    if success:
        print("🎉 Cookie update completed successfully!")
    else:
        print("ℹ️  No changes made")
