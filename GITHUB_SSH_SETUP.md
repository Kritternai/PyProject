# 🔑 การตั้งค่า SSH Key สำหรับ GitHub

## 🚨 ปัญหาที่พบ

```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

## 🔍 สาเหตุ

ไม่มี SSH key ที่ถูกต้องสำหรับ GitHub หรือ SSH key ยังไม่ได้ถูกเพิ่มใน GitHub account

## ✅ สิ่งที่ทำแล้ว

### **1. สร้าง SSH Key ใหม่**

```bash
ssh-keygen -t ed25519 -C "kbbk@macbook.local" -f ~/.ssh/id_ed25519
```

**ผลลัพธ์:**
- Private key: `~/.ssh/id_ed25519`
- Public key: `~/.ssh/id_ed25519.pub`

### **2. เริ่ม SSH Agent**

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### **3. สร้าง SSH Config**

ไฟล์: `~/.ssh/config`
```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
```

## 🔧 ขั้นตอนที่ต้องทำต่อไป

### **Step 1: คัดลอก Public Key**

```bash
cat ~/.ssh/id_ed25519.pub
```

**Public Key ที่ได้:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGtdrhwH4aSMXZiJhnzA9tJifwa8ZchN2dGjEwx4gXer kbbk@macbook.local
```

### **Step 2: เพิ่ม SSH Key ใน GitHub**

1. ไปที่ **GitHub.com** → **Settings** → **SSH and GPG keys**
2. คลิก **New SSH key**
3. ตั้งชื่อ: `MacBook Pro - PyProject`
4. คัดลอก public key ด้านบนไปวางใน **Key** field
5. คลิก **Add SSH key**

### **Step 3: ทดสอบ SSH Connection**

```bash
ssh -T git@github.com
```

**ผลลัพธ์ที่คาดหวัง:**
```
Hi Kritternai! You've successfully authenticated, but GitHub does not provide shell access.
```

### **Step 4: Push Code**

```bash
git add .
git commit -m "Fix database schema and authentication issues"
git push -u origin dev-web/migrations
```

## 🚀 วิธีแก้ไขแบบเร็ว (Alternative)

### **Option 1: ใช้ HTTPS แทน SSH**

```bash
# เปลี่ยน remote URL
git remote set-url origin https://github.com/Kritternai/PyProject.git

# Push code
git push -u origin dev-web/migrations
```

### **Option 2: ใช้ Personal Access Token**

1. ไปที่ **GitHub.com** → **Settings** → **Developer settings** → **Personal access tokens**
2. คลิก **Generate new token**
3. เลือก scopes: `repo`, `workflow`
4. คัดลอก token และใช้แทน password

```bash
git push -u origin dev-web/migrations
# Username: Kritternai
# Password: [Personal Access Token]
```

## 📱 การตั้งค่า SSH Key บน macOS

### **1. ตรวจสอบ SSH Key**

```bash
ls -la ~/.ssh/
```

### **2. เริ่ม SSH Agent**

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### **3. ทดสอบ Connection**

```bash
ssh -T git@github.com
```

### **4. ตรวจสอบ SSH Config**

```bash
cat ~/.ssh/config
```

## 🔒 Security Best Practices

- **ใช้ ED25519** - ปลอดภัยกว่า RSA
- **ตั้ง Passphrase** - เพิ่มความปลอดภัย
- **ใช้ SSH Agent** - ไม่ต้องพิมพ์ passphrase ทุกครั้ง
- **จำกัด Access** - ใช้ key เฉพาะ GitHub

## 🎯 Troubleshooting

### **ปัญหาที่พบบ่อย**

1. **Permission denied**
   - ตรวจสอบ SSH key ถูกเพิ่มใน GitHub หรือไม่
   - ตรวจสอบ SSH agent ทำงานหรือไม่

2. **Key not found**
   - ตรวจสอบ path ของ SSH key
   - ตรวจสอบ SSH config file

3. **Connection timeout**
   - ตรวจสอบ firewall settings
   - ตรวจสอบ network connection

## 🎉 สรุป

✅ **SSH Key สร้างแล้ว** - `~/.ssh/id_ed25519`
✅ **SSH Agent เริ่มแล้ว** - key ถูกเพิ่มแล้ว
✅ **SSH Config สร้างแล้ว** - `~/.ssh/config`

**ขั้นตอนต่อไป:**
1. คัดลอก public key ไปใส่ใน GitHub
2. ทดสอบ SSH connection
3. Push code ไปยัง repository

**ทดสอบ**: `ssh -T git@github.com`
