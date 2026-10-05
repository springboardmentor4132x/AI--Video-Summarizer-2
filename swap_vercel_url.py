import os, glob, re

frontend_dir = r'C:\Users\KHUSHI\OneDrive\Desktop\Project\AI--Video-Summarizer-2\frontend'
count = 0
for filepath in glob.glob(frontend_dir + '/**/*.ts*', recursive=True) + glob.glob(frontend_dir + '/**/*.js*', recursive=True):
    if 'node_modules' in filepath or '.next' in filepath:
        continue
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        
        if 'http://localhost:8000' in new_content:
            new_content = re.sub(
                r'\"http:\/\/localhost:8000', 
                r'(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "', 
                new_content
            )
            new_content = re.sub(
                r'\'http:\/\/localhost:8000', 
                r"(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '", 
                new_content
            )
            new_content = re.sub(
                r'\`http:\/\/localhost:8000', 
                r'`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}', 
                new_content
            )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {os.path.basename(filepath)}')
            count += 1

print(f'Updated {count} files for Vercel deployment.')
