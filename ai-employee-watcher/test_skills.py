"""
Test all Agent Skills
"""

from skills import *

print("="*60)
print("🧪 Testing Agent Skills")
print("="*60)

# Test 1: Read
print("\n1️⃣ Testing read_vault_file...")
dashboard = read_vault_file("Dashboard.md")
print(f"✅ Read {len(dashboard)} characters")

# Test 2: List folders
print("\n2️⃣ Testing list_vault_folder...")
inbox = list_vault_folder("Inbox")
print(f"✅ Inbox has {len(inbox)} items: {inbox}")

# Test 3: Get inbox summary
print("\n3️⃣ Testing get_inbox_summary...")
summary = get_inbox_summary()
print(f"✅ Summary: {summary}")

# Test 4: Create inbox item
print("\n4️⃣ Testing create_inbox_item...")
new_file = create_inbox_item(
    title="Test Agent Skill",
    content="This was created by the skills test",
    priority="high"
)
print(f"✅ Created: {new_file}")

# Test 5: Update dashboard
print("\n5️⃣ Testing update_dashboard_stats...")
result = update_dashboard_stats()
print(f"✅ {result}")

# Test 6: Move file
print("\n6️⃣ Testing move_vault_file...")
move_result = move_vault_file(new_file, "Inbox", "Done")
print(f"✅ {move_result}")

print("\n" + "="*60)
print("🎉 All Agent Skills Working!")
print("="*60)