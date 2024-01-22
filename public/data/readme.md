Every publication has a resource file. This file is a CSV file with three columns.

- **name**: The display name for the resource.
- **url**: The URL for this resource
- **icon**: The displayed icon key.

Every paper already has a stub resource file. The easiest way to find it
is by selecting the `Add resources` button on the vispubs website and then selecting
the resource file link. The filename is directly based on the publication's DOI, so
it is possible to locate the file with the DOI in the `paperLinks` folder.

For an example of a completed resource document, see https://github.com/Dev-Lan/vispubs/tree/main/public/data/paperLinks/10.1109/TVCG.2021.3114766. Which corresponds to https://www.vispubs.devinlange.com/?paper=10.1109%2FTVCG.2021.3114766.

When linking the paper document, please only provide links to the open-source preprint version of the paper.
I will only accept paper links that point to an open-access repository, such as osf.io or arxiv.org.
This policy is in place to prevent link-rot and copyright issues. If your paper is not already on an
open-source repository, now is a great time to do it :)

The order in the resource file will determine the order of links on the vispubs website.

There are currently six supported icons: `paper`, `video`, `code`, `website`, `data`, `other`.
These icons will be displayed in the detailed paper view and the paper list view. They will
also be used to determine which resources are available on each paper. For example, once
filtering is implemented, a user may filter to only papers that have a preprint version of
the `paper` linked.