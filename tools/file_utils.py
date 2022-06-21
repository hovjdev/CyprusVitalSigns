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


def get_latest_image(dirpath, valid_extensions=('jpg','jpeg','png')):
    """
    Get the latest image file in the given directory
    """

    # get filepaths of all files and dirs in the given dir
    valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
    # filter out directories, no-extension, and wrong extension files
    valid_files = [f for f in valid_files if '.' in f and \
        f.rsplit('.',1)[-1] in valid_extensions and os.path.isfile(f)]

    if not valid_files:
        raise ValueError("No valid images in %s" % dirpath)

    latest_image = max(valid_files, key=os.path.getmtime)
    return os.path.join(dirpath, latest_image)


if __name__ == "__main__":


    pass
