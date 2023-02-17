def get_child_folders(child_folders) -> list:
    folders = []
    for folder in child_folders:
        folders.append(folder)
        new_child_folders = folder.folders.all()
        if new_child_folders:
            folders.extend(get_child_folders(new_child_folders))
    return folders
