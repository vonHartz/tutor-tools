# Workflow

-   **For the initial checkout run `make checkout-or-update-all`.** This will automatically scrape the list of tutants if run for the first time and then clone all the subversions folder.
-   **If there is a change in the list of tutants, update via `load-tut-list`.** Then proceed with checkout/update of SVN folders.

-   **For grading a single sheet:**
    -   Create a file `.conf/tasks<sheetno>.json`, containing the maximum points per task.
    -   Run `make feedback<sheetno>`, e.g. `make feedback01` (note the leading zero) to update the folders and generate the feedback file.
    -   Correct the individual tutants' sheets and update the corresponding `feedback-tutor.txt` manually.
    -   Run `upload<sheetno>` to add the feedback file to SVN, commit it, aggregate the achieved points in json and push it to Daphne.

-   TODO: Might wanna change Tasks folder in Makefile to be different from conf folder.
