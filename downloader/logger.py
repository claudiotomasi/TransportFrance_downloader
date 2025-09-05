import os
import shutil

def merge_error_logs(output_folder):
    """Merge all per-thread error logs into a single file."""
    merged_file = os.path.join(output_folder, "errors.log")
    with open(merged_file, "w", encoding="utf-8") as outfile:
        for fname in os.listdir("."):
            if fname.startswith("errors_thread_") and fname.endswith(".log"):
                with open(fname, "r", encoding="utf-8") as infile:
                    shutil.copyfileobj(infile, outfile)
                os.remove(fname)

    with open(merged_file, "r", encoding="utf-8") as f:
        content = f.read()

    num_errors = len([p for p in content.split("\n\n") if "❌" in p])
    print(f"📄 Errors collected in: {merged_file}. {num_errors} found.")

    