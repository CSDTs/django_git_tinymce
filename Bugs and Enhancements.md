**Back-end**:
  - ~~Modify tag and sub-tag of repo (ModelForm)~~
  - ~~Fix create file form - wrong editor~~
  - ~~Template nav image absolut url~~
  - ~~Prefill rename file form~~
  - ~~file rename should be slugified/protected (don't allow ' or " etc..)~~ 
  - ~~Move submit button down in repo settings page~~
  - ~~remove gitusers model~~
  - ~~Configure CKEditor to allow script tag~~

  - Parse commit message
    - Show only file changed in commit view
      - use diff_to_tree()
      - http://www.pygit2.org/diff.html
      - current showing the file hex instead of the last commit hex that involves the file changed.

  - Indication of owner in render mode/page
  - Editable template


**Front-end**:
  - Folder detail view is asking for README.MD using relative URL causing 404
  - Link to subfolder should use repo.slug not repo.name.
    - example: Repo name = Quilting
               Repo slug = quilting
               http://127.0.0.1:8000/admin/quilting/img/ is different from
               http://127.0.0.1:8000/admin/Quilting/img/

  - Random folder go to broken
    - Uses filefetch api but does not handle 404 response which means couldn't locate the directory

  - Tag filter (grade level, subject). (API is done.)
  - Loading indication while forking
  - Admin link vs. index render link
  - Remove branch button
  - Folder drop info/handle
  - Auto complete user
  - Readme not embedded
  - Download image corrupt (suspect extention in CAP letters) - file: layout.js(256:165)
    - This can be handled by backend, easier.
  - Commit Log page broken
  - Subfoder view, base folder link in CAP letters


**Both**:
  - Delete folders
  - Hide .placeholder
  - Warn overwrite drag and drop upload
  - Static link change


**Enhancement**:
  - Limit tags / auto-complete