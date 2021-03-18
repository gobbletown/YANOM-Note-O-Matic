---
title: Settings used for - git flavoured markdown - gfm
creation_time: 2021-02-15 19:46
modified_time: 2021-03-16 23:05
---

```
gfm_markdown = True  # True generate github flavoured markdown (includes image sizing with a html <img tag), False generate strict markdown +pipe_tables -raw_html
links_as_URI = False  # True for file://link%20target style links, False for /link target style links
absolute_links = False  # True for absolute links, False for relative links
image_format_with_attributes = False  # True ![](media/image.png){width='image_size'}  DO NOT USE WITH gfm_markdown
obsidian_image_format = False  # True - ![|image_width](path to image), False  ![](media/image.png)
media_dir_name = 'media'  # name of the directory inside the produced directory where all images and attachments will be stored
md_file_ext = 'md'  # extension for produced markdown syntax note files
insert_title = True  # True to insert note title as a markdown heading at the first line, False to disable
insert_ctime = True  # True to insert note creation time to the beginning of the note text, False to disable
insert_mtime = True  # True to insert note modification time to the beginning of the note text, False to disable
creation_date_in_filename = False  # True to insert note creation time to the note file name, False to disable
tag_prepend = '#'  # string to prepend each tag in a tag list inside the note, default is empty
tag_delimiter = ', '  # string to delimit tags, default is comma separated list
no_spaces_in_tags = True  # True to replace spaces in tag names with '_', False to keep spaces
```

