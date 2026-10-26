import os

project_dir = "." 
output_file = "project_context.txt"

included_extensions = {".py", ".html", ".css", ".js", ".json", ".txt"}
ignored_dirs = {".git", "__pycache__", "venv", "env", "node_modules"}

with open(output_file, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in included_extensions:
                file_path = os.path.join(root, file)
                outfile.write(f"\n\n{'='*50}\n")
                outfile.write(f"FILE: {file_path}\n")
                outfile.write(f"{'='*50}\n\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"[Error reading file: {e}]")

print(f"تم تجميع المشروع بنجاح في ملف: {output_file}")
