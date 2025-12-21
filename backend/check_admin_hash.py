import sqlite3

db = sqlite3.connect('natpudan.db')
cursor = db.cursor()
cursor.execute('SELECT email, hashed_password FROM users WHERE email = ?', ('admin@admin.com',))
result = cursor.fetchone()

if result:
    email, password_hash = result
    print(f'Email: {email}')
    print(f'Hash (first 60 chars): {password_hash[:60]}')
    print(f'Hash length: {len(password_hash)}')
    print()
    
    if password_hash.startswith('$2'):
        print('✅ Format: BCRYPT')
        print('   This CAN be verified with bcrypt.checkpw()')
    elif len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash):
        print('❌ Format: SHA256 HEX')
        print('   This CANNOT be verified with bcrypt.checkpw()')
        print('   It would return False for any password!')
    elif len(password_hash) > 50:
        print('❓ Format: UNKNOWN/OTHER')
        print(f'   Pattern: {password_hash[:30]}...')
    else:
        print(f'⚠️  Hash seems too short: {len(password_hash)} chars')
else:
    print('❌ Admin user not found in database')

db.close()
