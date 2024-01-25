To add links for a publication update its resource file and submit a pull request, I will review them and push them to the website
periodically.

Every publication has a resource file that determines which
resource links are listed on the webpage. The file is structured
as a CSV with three components per link (name,url,icon).
The order of the links in this file determines
the order on the webpage.

- **name**: The display name for the resource.
- **url**: The URL for this resource
- **icon**: The displayed icon key.

Every paper already has a resource file. The easiest way to find it
is by selecting the `Add Resources` button on the vispubs website and then selecting
the resource file link. The filename is directly based on the publication's DOI, so
it is also possible to locate the file with the DOI in the `paperLinks` folder.

For an example of a completed resource document,
see https://github.com/Dev-Lan/vispubs/tree/main/public/data/paperLinks/10.1109/TVCG.2021.3114766.
Which corresponds to https://www.vispubs.devinlange.com/?paper=10.1109%2FTVCG.2021.3114766.

When linking the paper document, please only provide links to an open-source preprint version of the paper.
Links to an open-access repository, such as osf.io or arxiv.org, are _strongly preferred_
to PDFs hosted on personal websites.
If your paper is not already on an open-source repository, now is a great time to add it :)

There are currently six supported icons: `paper`, `video`, `code`, `project_website`, `data`, and `other`.
These icons will be displayed in the detailed paper view and the paper list view. They will
also be used to determine which resources are available on each paper. Soon, the website will support
filtering based on available resources.

To help with consistency on the site, please use the following naming conventions:

- `Project Website` or `Project Website with Demo` for project website landing pages.
- `Paper Preprint` for the open access preprint version of your paper.
- `Fast Forward` for 30-second preview videos of your paper.
