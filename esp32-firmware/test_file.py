def intersect_file_lists(source_file_list, downloaded_file_list):
    downloaded_ids = {file['id'] for file in downloaded_file_list}
    result = []

    for source_file in source_file_list:
        if source_file['id'] in downloaded_ids:
            for downloaded_file in downloaded_file_list:
                if source_file['id'] == downloaded_file['id']:
                    result.append({**source_file, **downloaded_file})
                    break

    return result

def test_intersects():
    source_file_list = [
        {"id": "1", "name": "file1"},
        {"id": "2", "name": "file2"},
        {"id": "3", "name": "file3"},
        {"id": "4", "name": "file4"},
    ]
    downloaded_file_list = [
        {"id": "2"},
        {"id": "4"},
    ]
    result = intersect_file_lists(source_file_list, downloaded_file_list)
    print(result)

test_intersects()