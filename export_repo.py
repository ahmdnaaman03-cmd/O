import os

def export_project_to_txt(output_filename="orderping_source_code.txt"):
    ignore_dirs = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode'}
    ignore_exts = {'.pyc', '.png', '.jpg', '.jpeg', '.pdf', '.sqlite3'}

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write("=== مشروع OrderPing - الكود المصدري ===\n\n")
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ignore_exts or file == output_filename or file == "export_repo.py":
                    continue

                filepath = os.path.join(root, file)
                outfile.write(f"\n{'='*50}\n")
                outfile.write(f"File Path: {filepath}\n")
                outfile.write(f"{'='*50}\n\n")

                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n")
                except Exception as e:
                    outfile.write(f"[تعذر قراءة الملف: {e}]\n")

    print(f"✅ تم تجميع الأكواد بنجاح في ملف: {output_filename}")

if __name__ == "__main__":
    export_project_to_txt()
