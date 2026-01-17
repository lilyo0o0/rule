import os
import re

def transform_line(line, is_cidr):
    # 去除首尾空格
    stripped = line.strip()
    
    # 1. 如果是注释行，保持原样（去除行尾换行符以便统一处理）
    if stripped.startswith('#'):
        return line.rstrip()

    # 2. 如果是 payload: 这一行，直接忽略
    if stripped.startswith('payload:'):
        return None

    # 3. 匹配格式 - 'content'
    # 使用正则匹配引号内的内容
    match = re.search(r"-\s*'(.*?)'", stripped)
    if match:
        content = match.group(1)
        
        # 如果文件名包含 cidr
        if is_cidr:
            return f"IP-CIDR,{content}"
        
        # 普通域名处理逻辑
        if content.startswith('+.'):
            # 转换为 DOMAIN-SUFFIX
            domain = content[2:] # 去掉 +.
            return f"DOMAIN-SUFFIX,{domain}"
        else:
            # 转换为 DOMAIN
            return f"DOMAIN,{content}"
    
    # 如果是不符合预期的行，返回 None 忽略（后续不处理）
    return None

def process_files():
    # 定义源目录和目标目录
    source_dir = 'temp_upstream'
    target_dir = 'txt'
    
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist!")
        return
    
    # 遍历源目录
    for filename in os.listdir(source_dir):
        # 排除 requirements 文件以及指定的 applications.txt
        if filename.endswith('.txt') and filename != 'requirements.txt' and filename != 'applications.txt':
            
            # 判断是否为 CIDR 文件
            is_cidr = 'cidr' in filename.lower()
            
            print(f"Processing {filename} (Mode: {'IP-CIDR' if is_cidr else 'Domain'})...")
            
            # 源文件和目标文件的完整路径
            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)
            
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    transformed = transform_line(line, is_cidr)
                    if transformed is not None:
                        new_lines.append(transformed)

                # 写入目标文件，确保最后有一个换行
                if new_lines:
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines) + '\n')
                    print(f"  ✓ Saved to {target_file}")
                else:
                    # 如果转换后文件为空（除payload外没内容），创建空文件
                    open(target_file, 'w').close()
                    print(f"  ✓ Created empty file: {target_file}")
                    
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")

if __name__ == "__main__":
    process_files()
