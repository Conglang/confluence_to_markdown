# Confluence-to-Markdown
Convert Confluence Html export to Hexo Markdown.

Logic almost identical to [Confluence-to-Github-Markdown](https://github.com/EWhite613/Confluence-to-Github-Markdown) of EWhite613. Rewrite in Python and make some changes to suit my needs.

## Requirements

**Must have pandoc command line tool.**

http://pandoc.org/installing.html

Make sure it was installed properly by doing `pandoc --version`.

## Export to HTML

Note that if the converter does not know how to handle a style, HTML to Markdown typically just leaves the HTML untouched (Markdown does allow for HTML tags).

Step by Step Guide

1. Go to the space and choose Space tools > Content Tools on the sidebar.
2. Choose Export. The option will be available only if you have the 'Export Space' permission.
3. Select HTML then choose Next.
4. Customize the export:
Select Normal Export to produce an HTML file containing all the pages that you have permission to view.
Select Custom Export if you want to export a subset of pages, or to exclude comments from the export.
5. ![Export Pages] (https://confluence.atlassian.com/conf54/files/428803470/confluence_spaceadmin_exportHTML.png)
6. Extract zip.
7. Open shell in extracted zip
8. Run `python confluence_html_to_markdown.py --input_dir "YOUR_INPUT_PATH" --output_dir "YOUR_OUTPUT_PATH"`.
