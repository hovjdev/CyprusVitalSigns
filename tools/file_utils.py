import os
import shutil



def create_dir(path):
    created=False
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
            created=True
    except Exception as e:
        print(str(e))
    return created

def delete_previous_files(path):
    try:
        if os.path.isdir(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {str(e)}')
    except Exception as e:
        print(str(e))
    return
